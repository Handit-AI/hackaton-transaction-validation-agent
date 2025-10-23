# LangGraph Parallel Execution Setup Guide

## Overview

This document provides specific instructions for implementing parallel execution of analyzer nodes in LangGraph for the fraud detection system.

---

## 1. Graph Structure for Parallel Execution

### 1.1 Visual Flow

```
                    START
                      |
                 Orchestrator
                      |
        ┌─────────────┴─────────────┐
        |     PARALLEL BRANCH       |
        |                           |
    ┌───┴───┬────┬────┬────┬──────┐
    |       |    |    |    |      |
Pattern  Behav  Vel  Merch  Geo
    |       |    |    |    |      |
    └───┬───┴────┴────┴────┴──────┘
        |                           |
        └─────────────┬─────────────┘
                      |
              Decision Aggregator
                      |
             Parse Final Decision
                      |
                     END
```

### 1.2 LangGraph Implementation Pattern

```python
from langgraph.graph import StateGraph
from langgraph.graph.graph import END

# Build graph with parallel execution
def build_fraud_detection_graph():
    graph = StateGraph(FraudDetectionState)

    # Add all nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("pattern_detector", pattern_detector_node)
    graph.add_node("behavioral_analyzer", behavioral_analyzer_node)
    graph.add_node("velocity_checker", velocity_checker_node)
    graph.add_node("merchant_risk_analyzer", merchant_risk_analyzer_node)
    graph.add_node("geographic_analyzer", geographic_analyzer_node)
    graph.add_node("decision_aggregator", decision_aggregator_node)

    # START to orchestrator
    graph.add_edge("START", "orchestrator")

    # PARALLEL BRANCHING from orchestrator
    graph.add_edge("orchestrator", "pattern_detector")
    graph.add_edge("orchestrator", "behavioral_analyzer")
    graph.add_edge("orchestrator", "velocity_checker")
    graph.add_edge("orchestrator", "merchant_risk_analyzer")
    graph.add_edge("orchestrator", "geographic_analyzer")

    # CONVERGENCE - all analyzers to aggregator
    graph.add_edge("pattern_detector", "decision_aggregator")
    graph.add_edge("behavioral_analyzer", "decision_aggregator")
    graph.add_edge("velocity_checker", "decision_aggregator")
    graph.add_edge("merchant_risk_analyzer", "decision_aggregator")
    graph.add_edge("geographic_analyzer", "decision_aggregator")

    # Final steps
    graph.add_edge("decision_aggregator", END)

    return graph.compile()
```

---

## 2. Node Implementations for Parallel Execution

### 2.1 Orchestrator Node - Prepares for Parallel Dispatch

```python
async def orchestrator_node(state: FraudDetectionState) -> FraudDetectionState:
    """
    Prepare transaction for parallel analysis.
    Sets up state for all analyzers to run simultaneously.
    """
    # Parse and enrich transaction
    transaction = state["raw_transaction"]

    # Validate and normalize
    parsed = parse_transaction(transaction)
    enriched = enrich_transaction(parsed)

    # Determine which analyzers to run
    analyzers_to_run = []

    # Core analyzers always run
    analyzers_to_run.extend([
        "pattern_detector",
        "behavioral_analyzer",
        "velocity_checker"
    ])

    # Conditional analyzers
    if enriched.get("merchant"):
        analyzers_to_run.append("merchant_risk_analyzer")

    if enriched.get("location") or enriched.get("ip_address"):
        analyzers_to_run.append("geographic_analyzer")

    # Update state for parallel execution
    state["parsed_transaction"] = parsed
    state["enriched_transaction"] = enriched
    state["analyzers_to_run"] = analyzers_to_run
    state["pending_nodes"] = analyzers_to_run.copy()
    state["current_stage"] = "parallel_analysis"

    # Initialize analyzer states
    for analyzer in analyzers_to_run:
        state["analyzer_states"][analyzer] = {
            "status": "pending",
            "started_at": None,
            "completed_at": None
        }

    return state
```

### 2.2 Analyzer Nodes - Run in Parallel

```python
async def pattern_detector_node(state: FraudDetectionState) -> FraudDetectionState:
    """
    Pattern detection analyzer - runs in parallel with other analyzers.
    """
    # Check if this analyzer should run
    if "pattern_detector" not in state.get("analyzers_to_run", []):
        return state  # Skip if not needed

    try:
        # Mark as started
        state["analyzer_states"]["pattern_detector"]["status"] = "running"
        state["analyzer_states"]["pattern_detector"]["started_at"] = time.time()

        # Get transaction data
        transaction = state["enriched_transaction"]

        # Perform analysis (LLM call)
        result = await analyze_patterns(transaction)

        # Update state with results
        state = update_analyzer_result(state, "pattern_detector", result)

        # Mark as completed
        state["analyzer_states"]["pattern_detector"]["status"] = "completed"
        state["analyzer_states"]["pattern_detector"]["completed_at"] = time.time()

    except Exception as e:
        # Handle failure gracefully
        state = mark_analyzer_failed(state, "pattern_detector", str(e))

    return state

# Similar implementation for other analyzer nodes...
```

### 2.3 Decision Aggregator - Waits for Parallel Results

```python
async def decision_aggregator_node(state: FraudDetectionState) -> FraudDetectionState:
    """
    Aggregates results from all parallel analyzers.
    This node automatically waits for all parallel branches to complete.
    """
    # LangGraph ensures all incoming edges complete before running this node

    # Collect all analyzer results
    analyzer_results = state.get("analyzer_results", {})

    # Check minimum analyzers requirement
    completed_analyzers = [
        name for name, result in analyzer_results.items()
        if result.get("status") != "failed"
    ]

    if len(completed_analyzers) < 3:
        # Not enough analyzers completed
        state["final_decision"] = {
            "decision": "DECLINE",
            "reasoning": "Insufficient analyzer coverage",
            "risk_score": 100
        }
        return state

    # Calculate weighted risk score
    weighted_score = calculate_weighted_risk_score(state)

    # Determine consensus
    consensus = get_analyzer_consensus(state)

    # Generate final decision
    decision = determine_decision(weighted_score)
    reasoning = generate_reasoning(analyzer_results, decision, weighted_score)

    # Update state with aggregated decision
    state["aggregated_analysis"] = {
        "weighted_risk_score": weighted_score,
        "consensus": consensus,
        "individual_scores": state["risk_scores"],
        "analyzer_coverage": len(completed_analyzers) / len(state["analyzers_to_run"])
    }

    state = set_final_decision(
        state,
        decision=decision,
        risk_score=weighted_score,
        reasoning=reasoning,
        confidence=consensus["agreement_rate"]
    )

    return state
```

---

## 3. Conditional Execution Within Parallel Flow

### 3.1 Dynamic Analyzer Selection

Instead of using conditional edges, we can make nodes check if they should run:

```python
async def geographic_analyzer_node(state: FraudDetectionState) -> FraudDetectionState:
    """
    Geographic analyzer - only runs if location data is available.
    """
    # Self-check if should run
    if not should_run_geographic_analyzer(state):
        # Mark as skipped
        state["analyzer_states"]["geographic_analyzer"] = {
            "status": "skipped",
            "reason": "No location data available"
        }
        # Provide neutral score
        state["risk_scores"]["geographic_analyzer"] = 50.0
        return state

    # Proceed with analysis...
    # [Rest of implementation]

def should_run_geographic_analyzer(state: FraudDetectionState) -> bool:
    """Check if geographic analyzer should run."""
    transaction = state.get("enriched_transaction", {})
    return bool(
        transaction.get("location") or
        transaction.get("ip_address") or
        transaction.get("previous_location")
    )
```

---

## 4. Timeout and Error Handling

### 4.1 Implementing Timeouts for Parallel Nodes

```python
import asyncio
from typing import Any, Dict

async def pattern_detector_with_timeout(state: FraudDetectionState) -> FraudDetectionState:
    """Pattern detector with timeout handling."""
    try:
        # Run with timeout
        result = await asyncio.wait_for(
            analyze_patterns(state["enriched_transaction"]),
            timeout=5.0  # 5 second timeout
        )
        state = update_analyzer_result(state, "pattern_detector", result)

    except asyncio.TimeoutError:
        # Timeout occurred
        state = mark_analyzer_failed(state, "pattern_detector", "Timeout after 5 seconds")
        # Provide default medium-risk score
        state["risk_scores"]["pattern_detector"] = 50.0

    except Exception as e:
        # Other error
        state = mark_analyzer_failed(state, "pattern_detector", str(e))
        state["risk_scores"]["pattern_detector"] = 50.0

    return state
```

### 4.2 Partial Results Handling

```python
async def decision_aggregator_with_partial_results(state: FraudDetectionState) -> FraudDetectionState:
    """Aggregator that can work with partial results."""

    analyzer_results = state.get("analyzer_results", {})
    successful_analyzers = []
    failed_analyzers = []

    for analyzer in state["analyzers_to_run"]:
        if analyzer in analyzer_results and analyzer_results[analyzer].get("status") != "failed":
            successful_analyzers.append(analyzer)
        else:
            failed_analyzers.append(analyzer)

    # Adjust weights for missing analyzers
    adjusted_weights = recalculate_weights(successful_analyzers)

    # Calculate score with available results
    weighted_score = 0.0
    for analyzer in successful_analyzers:
        score = state["risk_scores"].get(analyzer, 50.0)
        weight = adjusted_weights.get(analyzer, 0.0)
        weighted_score += score * weight

    # Add penalty for missing analyzers
    coverage_penalty = len(failed_analyzers) * 5  # 5 points per failed analyzer
    weighted_score = min(100, weighted_score + coverage_penalty)

    # Continue with decision...
```

---

## 5. State Management for Parallel Execution

### 5.1 Reducer Functions for Parallel Updates

```python
# In state definition, use proper reducers for parallel updates

class FraudDetectionState(TypedDict):
    # These fields can be updated in parallel without conflicts
    analyzer_results: Annotated[Dict[str, Dict], merge_dicts]
    risk_scores: Annotated[Dict[str, float], merge_dicts]

    # These accumulate findings from all analyzers
    all_findings: Annotated[List[str], extend_list]

    # Track which nodes have completed
    completed_nodes: Annotated[Set[str], union_sets]

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries without conflicts."""
    return {**dict1, **dict2}

def extend_list(list1: List, list2: List) -> List:
    """Extend list with new items."""
    return list1 + list2

def union_sets(set1: Set, set2: Set) -> Set:
    """Union of two sets."""
    return set1.union(set2)
```

---

## 6. Testing Parallel Execution

### 6.1 Verify Parallel Execution

```python
async def test_parallel_execution():
    """Test that analyzers run in parallel."""

    # Create test transaction
    test_transaction = {
        "user_id": "test_user",
        "amount": 1000,
        "merchant": "Test Merchant",
        "location": "Test Location"
    }

    # Create initial state
    state = create_initial_fraud_state(test_transaction)

    # Build and run graph
    graph = build_fraud_detection_graph()
    result = await graph.ainvoke(state)

    # Verify parallel execution by checking timestamps
    timestamps = result["analysis_timestamps"]

    # Check that analyzer start times are very close (within 100ms)
    start_times = [
        timestamps[analyzer]["started_at"]
        for analyzer in ["pattern_detector", "behavioral_analyzer", "velocity_checker"]
        if analyzer in timestamps
    ]

    if start_times:
        time_spread = max(start_times) - min(start_times)
        assert time_spread < 0.1, f"Analyzers did not run in parallel. Time spread: {time_spread}s"

    # Verify all analyzers completed
    for analyzer in result["analyzers_to_run"]:
        assert analyzer in result["analyzer_results"], f"{analyzer} did not complete"

    print("✅ Parallel execution verified")
```

### 6.2 Benchmark Performance

```python
import time

async def benchmark_parallel_vs_sequential():
    """Compare parallel vs sequential execution times."""

    test_transaction = create_test_transaction()

    # Parallel execution
    start = time.time()
    parallel_graph = build_fraud_detection_graph()  # Parallel config
    parallel_result = await parallel_graph.ainvoke(test_transaction)
    parallel_time = time.time() - start

    # Sequential execution (for comparison)
    start = time.time()
    sequential_graph = build_sequential_graph()  # Sequential config
    sequential_result = await sequential_graph.ainvoke(test_transaction)
    sequential_time = time.time() - start

    print(f"Parallel execution: {parallel_time:.2f}s")
    print(f"Sequential execution: {sequential_time:.2f}s")
    print(f"Speed improvement: {(sequential_time/parallel_time - 1)*100:.1f}%")

    # Verify same decision reached
    assert parallel_result["final_decision"]["decision"] == sequential_result["final_decision"]["decision"]
```

---

## 7. Production Considerations

### 7.1 Resource Management

```python
# Limit concurrent executions to prevent resource exhaustion
import asyncio

class RateLimitedGraph:
    def __init__(self, graph, max_concurrent=10):
        self.graph = graph
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def ainvoke(self, state):
        async with self.semaphore:
            return await self.graph.ainvoke(state)
```

### 7.2 Monitoring Parallel Execution

```python
def add_parallel_monitoring(state: FraudDetectionState) -> None:
    """Add monitoring metrics for parallel execution."""

    metrics = {
        "parallel_execution_time": state["total_execution_time"],
        "analyzers_run": len(state["completed_nodes"]),
        "analyzers_failed": len(state["failed_nodes"]),
        "parallel_efficiency": calculate_parallel_efficiency(state),
        "coverage_rate": len(state["completed_nodes"]) / len(state["analyzers_to_run"])
    }

    # Log to monitoring service
    log_metrics(metrics)
```

---

## 8. Key Implementation Points

### Critical Success Factors:

1. **State Isolation**: Each analyzer only reads from state, writes to unique keys
2. **No Dependencies**: Analyzers don't depend on each other's outputs
3. **Proper Reducers**: Use correct reducer functions for parallel state updates
4. **Error Resilience**: Failed analyzers don't block the entire flow
5. **Timeout Management**: Each analyzer has independent timeout
6. **Result Aggregation**: Aggregator waits for all branches automatically in LangGraph

### Common Pitfalls to Avoid:

1. **State Conflicts**: Don't write to same state keys from parallel nodes
2. **Sequential Dependencies**: Don't make analyzers depend on each other
3. **Blocking Operations**: Use async/await properly in all nodes
4. **Missing Results**: Handle cases where some analyzers fail
5. **Resource Exhaustion**: Limit concurrent graph executions

---

## Conclusion

This setup enables true parallel execution of analyzer nodes in LangGraph, reducing total processing time from ~15 seconds (sequential) to ~3-5 seconds (parallel) while maintaining decision quality and system resilience.
