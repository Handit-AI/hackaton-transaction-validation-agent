"""
State definition for risk_manager LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from operator import add

class AgentState(TypedDict):
    """
    State definition for the fraud detection agent graph.

    This defines the structure of data that flows through the graph.
    Supports both sequential and parallel execution of analyzer nodes.
    """
    # Input data - can be updated by multiple nodes
    input: Annotated[Any, lambda x, y: y]  # Last writer wins

    # Messages for conversation
    messages: Annotated[List[BaseMessage], add]

    # Context data - can be updated by multiple nodes
    context: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]  # Merge dictionaries

    # Results from each stage - can be updated by multiple nodes
    results: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]  # Merge dictionaries

    # Current stage - can be updated by multiple nodes
    current_stage: Annotated[Optional[str], lambda x, y: y]  # Last writer wins

    # Error information - can be updated by multiple nodes
    error: Annotated[Optional[str], lambda x, y: y]  # Last writer wins

    # Metadata - can be updated by multiple nodes
    metadata: Annotated[Dict[str, Any], lambda x, y: {**x, **y}]  # Merge dictionaries

    # ========== FRAUD DETECTION SPECIFIC FIELDS ==========
    # Transaction data
    transaction_data: Annotated[Optional[Dict[str, Any]], lambda x, y: y]  # Parsed transaction
    enriched_transaction: Annotated[Optional[Dict[str, Any]], lambda x, y: y]  # Enriched with risk factors

    # Analyzer outputs
    analyzer_results: Annotated[Dict[str, Dict[str, Any]], lambda x, y: {**x, **y}]  # Results from each analyzer
    risk_scores: Annotated[Dict[str, float], lambda x, y: {**x, **y}]  # Risk scores from each analyzer

    # Decision fields
    aggregated_decision: Annotated[Optional[Dict[str, Any]], lambda x, y: y]  # Aggregated analysis
    final_decision: Annotated[Optional[str], lambda x, y: y]  # APPROVE/REVIEW/DECLINE

    # Execution tracking
    analyzers_to_run: Annotated[List[str], lambda x, y: y]  # Which analyzers should run
    completed_analyzers: Annotated[List[str], lambda x, y: x + y if x else y]  # Accumulate completed

def create_initial_state(input_data: Any, **kwargs) -> AgentState:
    """
    Create initial state for the fraud detection graph.

    Args:
        input_data: Initial input data (transaction to analyze)
        **kwargs: Additional state parameters

    Returns:
        Initial agent state
    """
    from langchain_core.messages import HumanMessage
    import time

    return AgentState(
        input=input_data,
        messages=[HumanMessage(content=str(input_data))],
        context=kwargs.get("context", {}),
        results=kwargs.get("results", {}),
        current_stage=kwargs.get("current_stage", None),
        error=kwargs.get("error", None),
        metadata=kwargs.get("metadata", {"start_time": time.time()}),
        # Fraud detection specific fields
        transaction_data=None,
        enriched_transaction=None,
        analyzer_results={},
        risk_scores={},
        aggregated_decision=None,
        final_decision=None,
        analyzers_to_run=[],
        completed_analyzers=[]
    )

def update_state(current_state: AgentState, **updates) -> AgentState:
    """
    Update the current state with new values.

    Args:
        current_state: Current state
        **updates: State updates

    Returns:
        Updated state
    """
    return AgentState(
        input=updates.get("input", current_state["input"]),
        messages=updates.get("messages", current_state["messages"]),
        context=updates.get("context", current_state["context"]),
        results=updates.get("results", current_state["results"]),
        current_stage=updates.get("current_stage", current_state["current_stage"]),
        error=updates.get("error", current_state["error"]),
        metadata=updates.get("metadata", current_state["metadata"]),
        # Fraud detection fields
        transaction_data=updates.get("transaction_data", current_state.get("transaction_data")),
        enriched_transaction=updates.get("enriched_transaction", current_state.get("enriched_transaction")),
        analyzer_results=updates.get("analyzer_results", current_state.get("analyzer_results", {})),
        risk_scores=updates.get("risk_scores", current_state.get("risk_scores", {})),
        aggregated_decision=updates.get("aggregated_decision", current_state.get("aggregated_decision")),
        final_decision=updates.get("final_decision", current_state.get("final_decision")),
        analyzers_to_run=updates.get("analyzers_to_run", current_state.get("analyzers_to_run", [])),
        completed_analyzers=updates.get("completed_analyzers", current_state.get("completed_analyzers", []))
    )

def get_stage_result(state: AgentState, stage: str) -> Any:
    """
    Get result from a specific stage.
    
    Args:
        state: Current state
        stage: Stage name
        
    Returns:
        Stage result or None
    """
    return state["results"].get(stage)

def set_stage_result(state: AgentState, stage: str, result: Any) -> AgentState:
    """
    Set result for a specific stage.
    
    Args:
        state: Current state
        stage: Stage name
        result: Stage result
        
    Returns:
        Updated state
    """
    updated_results = state["results"].copy()
    updated_results[stage] = result
    
    return update_state(state, results=updated_results, current_stage=stage)

def add_message(state: AgentState, message: BaseMessage) -> AgentState:
    """
    Add a message to the conversation.
    
    Args:
        state: Current state
        message: Message to add
        
    Returns:
        Updated state
    """
    updated_messages = state["messages"] + [message]
    return update_state(state, messages=updated_messages)

def set_error(state: AgentState, error: str) -> AgentState:
    """
    Set error in the state.
    
    Args:
        state: Current state
        error: Error message
        
    Returns:
        Updated state
    """
    return update_state(state, error=error)

def clear_error(state: AgentState) -> AgentState:
    """
    Clear error from the state.

    Args:
        state: Current state

    Returns:
        Updated state
    """
    return update_state(state, error=None)


# ========== FRAUD DETECTION SPECIFIC HELPERS ==========

def update_analyzer_result(state: AgentState, analyzer_name: str, result: Dict[str, Any]) -> AgentState:
    """
    Update state with analyzer result.

    Args:
        state: Current state
        analyzer_name: Name of the analyzer
        result: Analyzer output

    Returns:
        Updated state
    """
    # Update analyzer results
    analyzer_results = state.get("analyzer_results", {}).copy()
    analyzer_results[analyzer_name] = result

    # Extract and store risk score
    risk_scores = state.get("risk_scores", {}).copy()
    if "risk_score" in result:
        risk_scores[analyzer_name] = result["risk_score"]

    # Mark as completed
    completed_analyzers = state.get("completed_analyzers", []) + [analyzer_name]

    return update_state(
        state,
        analyzer_results=analyzer_results,
        risk_scores=risk_scores,
        completed_analyzers=completed_analyzers
    )


def calculate_weighted_risk_score(state: AgentState, weights: Dict[str, float]) -> float:
    """
    Calculate weighted average risk score from all analyzers.

    Args:
        state: Current state
        weights: Dictionary of analyzer weights

    Returns:
        Weighted risk score (0-100)
    """
    risk_scores = state.get("risk_scores", {})
    total_score = 0.0
    total_weight = 0.0

    for analyzer, weight in weights.items():
        if analyzer in risk_scores:
            score = risk_scores[analyzer]
            total_score += score * weight
            total_weight += weight

    # Normalize if not all analyzers ran
    if total_weight > 0:
        return total_score / total_weight
    else:
        return 50.0  # Default medium risk


def determine_decision(risk_score: float, thresholds: Dict[str, int]) -> str:
    """
    Convert risk score to decision based on thresholds.

    Args:
        risk_score: Calculated risk score
        thresholds: Dictionary with decline/review/approve thresholds

    Returns:
        Decision string: APPROVE, REVIEW, or DECLINE
    """
    if risk_score >= thresholds["decline"]:
        return "DECLINE"
    elif risk_score >= thresholds["review"]:
        return "REVIEW"
    else:
        return "APPROVE"
