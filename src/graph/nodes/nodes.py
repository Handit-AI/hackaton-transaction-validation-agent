"""
Graph orchestration for risk_manager LangGraph
This file handles how nodes interact with each other and wraps node classes as LangGraph functions.
"""

from typing import Dict, Any, Callable
from langchain_core.messages import AIMessage
from handit_ai import tracing
import asyncio

from ...config import Config
from ...state import AgentState, set_stage_result, add_message, set_error, clear_error

# Import node classes from /src/nodes/
from ...nodes.llm.pattern_detector.processor import PatternDetectorLLMNode
from ...nodes.llm.behavioral_analizer.processor import BehavioralAnalizerLLMNode
from ...nodes.llm.velocity_checker.processor import VelocityCheckerLLMNode
from ...nodes.llm.merchant_risk_analizer.processor import MerchantRiskAnalizerLLMNode
from ...nodes.llm.geographic_analizer.processor import GeographicAnalizerLLMNode
from ...nodes.llm.decision_aggregator.processor import DecisionAggregatorLLMNode


# Global node instances (initialized once)
_node_instances = {}

def _get_node_instance(node_name: str, node_type: str = "llm"):
    """
    Get or create a node instance (singleton pattern).
    
    Args:
        node_name: Name of the node
        node_type: Type of node ('llm' or 'tool')
        
    Returns:
        Node instance
    """
    global _node_instances
    key = f"{node_name}_{node_type}"
    
    if key not in _node_instances:
        config = Config()
        if node_type == "llm":
            # Dynamic import for LLM nodes
            class_name = f"{''.join(word.capitalize() for word in node_name.replace('-', '_').split('_'))}LLMNode"
            module_path = f"src.nodes.llm.{node_name.replace('-', '_')}.processor"
            module = __import__(module_path, fromlist=[class_name])
            node_class = getattr(module, class_name)
            _node_instances[key] = node_class(config)
        else:
            # Dynamic import for Tool nodes
            class_name = f"{''.join(word.capitalize() for word in node_name.replace('-', '_').split('_'))}ToolNode"
            module_path = f"src.nodes.tools.{node_name.replace('-', '_')}.processor"
            module = __import__(module_path, fromlist=[class_name])
            node_class = getattr(module, class_name)
            _node_instances[key] = node_class(config)
    
    return _node_instances[key]

# LangGraph node functions that wrap node classes

async def orchestrator_node(state: AgentState) -> AgentState:
    """
    Orchestrator node that parses transaction and prepares for parallel analysis.
    This is the first node that dispatches work to all analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with parsed transaction and analyzer configuration
    """
    try:
        from ...state import update_state
        import json

        # Get transaction input
        input_data = state.get("input", {})

        # Parse transaction data
        if isinstance(input_data, str):
            try:
                transaction = json.loads(input_data)
            except json.JSONDecodeError:
                transaction = {"raw_data": input_data}
        else:
            transaction = input_data

        # Normalize transaction data from various formats
        normalized = {}

        # Extract basic fields
        normalized["user_id"] = (
            transaction.get("user_id") or
            transaction.get("customer", {}).get("customer_id") or
            transaction.get("customer_id") or
            f"user_{transaction.get('transaction_id', 'unknown')[:8]}"
        )

        normalized["user_age_days"] = (
            transaction.get("user_age_days") or
            transaction.get("customer", {}).get("age_of_account_days") or
            transaction.get("age_of_account_days") or
            180  # default
        )

        normalized["total_transactions"] = (
            transaction.get("total_transactions") or
            transaction.get("historical_stats", {}).get("total_lifetime_transactions") or
            10  # default
        )

        normalized["amount"] = (
            transaction.get("amount") or
            transaction.get("financial", {}).get("amount") or
            100.0  # default
        )

        normalized["time"] = (
            transaction.get("time") or
            transaction.get("transaction", {}).get("transaction_datetime", "14:00")[:5] or
            "14:00"
        )

        normalized["merchant"] = (
            transaction.get("merchant") or
            transaction.get("merchant_name") or
            transaction.get("merchant", {}).get("merchant_name") or
            transaction.get("merchant_data", {}).get("merchant_name") or
            "Unknown Merchant"
        )

        # Extract merchant category (MCC) for risk assessment
        normalized["merchant_category_code"] = (
            transaction.get("merchant_category_code") or
            transaction.get("merchant", {}).get("merchant_category_code") or
            transaction.get("merchant_data", {}).get("merchant_category_code") or
            "0000"  # default unknown
        )

        normalized["merchant_category"] = (
            transaction.get("merchant_category") or
            transaction.get("merchant", {}).get("merchant_category") or
            transaction.get("merchant_data", {}).get("merchant_category") or
            "Unknown"
        )

        normalized["location"] = (
            transaction.get("location") or
            f"{transaction.get('location', {}).get('transaction_city', '')}, {transaction.get('location', {}).get('transaction_country', '')}" if isinstance(transaction.get('location'), dict) else
            transaction.get("location_data", {}).get("transaction_city") or
            "Unknown"
        )

        normalized["previous_location"] = (
            transaction.get("previous_location") or
            transaction.get("behavioral_profile", {}).get("home_location", {}).get("city") or
            normalized["location"]  # default to current location
        )

        # Add additional transaction context if present
        normalized["transaction_id"] = transaction.get("transaction_id") or transaction.get("transaction", {}).get("transaction_id")
        normalized["transaction_type"] = transaction.get("transaction_type") or transaction.get("transaction", {}).get("transaction_type") or "PURCHASE"
        normalized["currency"] = transaction.get("currency") or transaction.get("financial", {}).get("currency") or "USD"

        # Card data (without sensitive info)
        normalized["card_data"] = transaction.get("card") or transaction.get("card_data", {})
        normalized["card_brand"] = transaction.get("card_brand") or transaction.get("card", {}).get("card_brand")
        normalized["card_type"] = transaction.get("card_type") or transaction.get("card", {}).get("card_type")

        # Device and authentication data
        normalized["device_data"] = transaction.get("device") or transaction.get("device_data", {})
        normalized["authentication_data"] = transaction.get("authentication") or transaction.get("authentication_data", {})

        # Velocity counters (these are computed from history, not risk scores)
        normalized["velocity_counters"] = transaction.get("velocity_counters", {})

        # Session data (behavioral, not risk)
        normalized["session_data"] = transaction.get("session") or transaction.get("session_data", {})

        # Behavioral profile (historical patterns, not scores)
        normalized["behavioral_profile"] = transaction.get("behavioral_profile", {})

        # Compute basic risk factors based on transaction characteristics (let analyzers determine actual risk)
        enriched = normalized.copy()
        enriched["computed_risk_factors"] = {
            "is_new_user": normalized["user_age_days"] < 90,
            "is_very_new_user": normalized["user_age_days"] < 7,
            "is_high_amount": normalized["amount"] > 1000,
            "is_very_high_amount": normalized["amount"] > 5000,
            "is_night_time": is_suspicious_time(normalized["time"]),
            "has_location_change": normalized.get("previous_location") != normalized.get("location"),
            "high_velocity": normalized.get("velocity_counters", {}).get("transactions_last_hour", 0) > 5,
            "many_declines": normalized.get("velocity_counters", {}).get("declined_transactions_last_24h", 0) > 3,
            "failed_authentication": normalized.get("authentication_data", {}).get("authentication_status") == "FAILED",
            "no_3ds": normalized.get("authentication_data", {}).get("authentication_method") == "NONE",
            "vpn_detected": normalized.get("device_data", {}).get("vpn_flag", False),
            "password_reset_recent": normalized.get("session_data", {}).get("password_reset_flag", False),
            "multiple_login_attempts": normalized.get("session_data", {}).get("login_attempts", 1) > 2
        }

        # Determine which analyzers to run (all for now in parallel)
        analyzers_to_run = [
            "pattern_detector",
            "behavioral_analizer",
            "velocity_checker",
            "merchant_risk_analizer",
            "geographic_analizer"
        ]

        # Update state
        state = update_state(
            state,
            transaction_data=transaction,
            enriched_transaction=enriched,
            analyzers_to_run=analyzers_to_run,
            current_stage="orchestrator"
        )

        # Add message
        message = AIMessage(content=f"Orchestrator: Dispatching transaction to {len(analyzers_to_run)} parallel analyzers")
        state = add_message(state, message)

        # Store in results for backward compatibility
        state = set_stage_result(state, "orchestrator", {
            "transaction": transaction,
            "enriched": enriched,
            "analyzers_dispatched": analyzers_to_run
        })

        return state

    except Exception as e:
        return set_error(state, f"Orchestrator error: {str(e)}")


def is_suspicious_time(time_str: str) -> bool:
    """Check if transaction time is suspicious (1 AM - 5 AM)"""
    try:
        hour = int(time_str.split(":")[0])
        return 1 <= hour <= 5
    except:
        return False




async def pattern_detector_node(state: AgentState) -> AgentState:
    """
    Pattern Detector node - analyzes transaction for known fraud patterns.
    Runs in parallel with other analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with pattern detection results
    """
    try:
        from ...state import update_analyzer_result
        import json

        # Get node instance
        node_instance = _get_node_instance("pattern_detector", "llm")

        # Get enriched transaction data
        transaction = state.get("enriched_transaction") or state.get("transaction_data") or state.get("input", {})

        # Prepare input for the LLM - include transaction details
        processing_input = json.dumps({
            "transaction": transaction,
            "analysis_type": "pattern_detection",
            "focus": "fraud_patterns"
        })

        # Call the actual node class - it will return text analysis
        result = await node_instance.run(processing_input)

        # Store the text result directly
        result_text = str(result) if result else "No patterns detected."

        # Update state with analyzer results (as text)
        state = update_analyzer_result(state, "pattern_detector", result_text)
        state = set_stage_result(state, "pattern_detector", result_text)

        # Add AI message
        message = AIMessage(content=f"Pattern Detector completed analysis")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"PatternDetector node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def behavioral_analizer_node(state: AgentState) -> AgentState:
    """
    Behavioral Analyzer node - detects anomalies from user behavior baseline.
    Runs in parallel with other analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with behavioral analysis results
    """
    try:
        from ...state import update_analyzer_result
        import json

        # Get node instance
        node_instance = _get_node_instance("behavioral_analizer", "llm")

        # Get enriched transaction data
        transaction = state.get("enriched_transaction") or state.get("transaction_data") or state.get("input", {})

        # Prepare input for the LLM - include transaction details
        processing_input = json.dumps({
            "transaction": transaction,
            "analysis_type": "behavioral_analysis",
            "focus": "user_behavior_deviations"
        })

        # Call the actual node class - it will return text analysis
        result = await node_instance.run(processing_input)

        # Store the text result directly
        result_text = str(result) if result else "No behavioral anomalies detected."

        # Update state with analyzer results (as text)
        state = update_analyzer_result(state, "behavioral_analizer", result_text)
        state = set_stage_result(state, "behavioral_analizer", result_text)

        # Add AI message
        message = AIMessage(content=f"Behavioral Analyzer completed analysis")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"BehavioralAnalizer node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def velocity_checker_node(state: AgentState) -> AgentState:
    """
    Velocity Checker node - detects rapid-fire attacks and velocity abuse.
    Runs in parallel with other analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with velocity analysis results
    """
    try:
        from ...state import update_analyzer_result
        import json

        # Get node instance
        node_instance = _get_node_instance("velocity_checker", "llm")

        # Get enriched transaction data
        transaction = state.get("enriched_transaction") or state.get("transaction_data") or state.get("input", {})

        # Prepare input for the LLM - include transaction details
        processing_input = json.dumps({
            "transaction": transaction,
            "analysis_type": "velocity_analysis",
            "focus": "transaction_velocity_patterns"
        })

        # Call the actual node class - it will return text analysis
        result = await node_instance.run(processing_input)

        # Store the text result directly
        result_text = str(result) if result else "No velocity issues detected."

        # Update state with analyzer results (as text)
        state = update_analyzer_result(state, "velocity_checker", result_text)
        state = set_stage_result(state, "velocity_checker", result_text)

        # Add AI message
        message = AIMessage(content=f"Velocity Checker completed analysis")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"VelocityChecker node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def merchant_risk_analizer_node(state: AgentState) -> AgentState:
    """
    Merchant Risk Analyzer node - assesses merchant trustworthiness.
    Runs in parallel with other analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with merchant risk analysis results
    """
    try:
        from ...state import update_analyzer_result
        import json

        # Get node instance
        node_instance = _get_node_instance("merchant_risk_analizer", "llm")

        # Get enriched transaction data
        transaction = state.get("enriched_transaction") or state.get("transaction_data") or state.get("input", {})

        # Prepare input for the LLM - include transaction details
        processing_input = json.dumps({
            "transaction": transaction,
            "analysis_type": "merchant_risk_analysis",
            "focus": "merchant_trustworthiness"
        })

        # Call the actual node class - it will return text analysis
        result = await node_instance.run(processing_input)

        # Store the text result directly
        result_text = str(result) if result else "Merchant appears legitimate."

        # Update state with analyzer results (as text)
        state = update_analyzer_result(state, "merchant_risk_analizer", result_text)
        state = set_stage_result(state, "merchant_risk_analizer", result_text)

        # Add AI message
        message = AIMessage(content=f"Merchant Risk Analyzer completed analysis")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"MerchantRiskAnalizer node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def geographic_analizer_node(state: AgentState) -> AgentState:
    """
    Geographic Analyzer node - detects location-based fraud and impossible travel.
    Runs in parallel with other analyzer nodes.

    Args:
        state: Current agent state

    Returns:
        Updated state with geographic analysis results
    """
    try:
        from ...state import update_analyzer_result
        import json

        # Get node instance
        node_instance = _get_node_instance("geographic_analizer", "llm")

        # Get enriched transaction data
        transaction = state.get("enriched_transaction") or state.get("transaction_data") or state.get("input", {})

        # Prepare input for the LLM - include transaction details
        processing_input = json.dumps({
            "transaction": transaction,
            "analysis_type": "geographic_analysis",
            "focus": "location_based_fraud"
        })

        # Call the actual node class - it will return text analysis
        result = await node_instance.run(processing_input)

        # Store the text result directly
        result_text = str(result) if result else "Location appears normal."

        # Update state with analyzer results (as text)
        state = update_analyzer_result(state, "geographic_analizer", result_text)
        state = set_stage_result(state, "geographic_analizer", result_text)

        # Add AI message
        message = AIMessage(content=f"Geographic Analyzer completed analysis")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"GeographicAnalizer node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def decision_aggregator_node(state: AgentState) -> AgentState:
    """
    Decision Aggregator node - combines all analyzer text results into final JSON decision.
    Uses OpenAI's JSON schema feature for structured output.

    Args:
        state: Current agent state

    Returns:
        Updated state with aggregated decision in JSON format
    """
    try:
        import json
        import time
        from ...config import Config

        config = Config()

        # Get all analyzer results (text from each analyzer)
        analyzer_results = state.get("analyzer_results", {})
        completed_analyzers = state.get("completed_analyzers", [])

        # Get transaction details
        transaction = state.get("enriched_transaction") or state.get("transaction_data", {})

        # Prepare all analyzer texts for the aggregator
        analyzer_summaries = []
        for analyzer_name in completed_analyzers:
            result = analyzer_results.get(analyzer_name)
            if result:
                analyzer_summaries.append(f"[{analyzer_name.replace('_', ' ').title()}]: {result}")

        # If we don't have enough analyzers, create error response
        if len(completed_analyzers) < config.min_analyzers_required:
            final_output = {
                "final_decision": "DECLINE",
                "conclusion": "Insufficient analysis completed - declining transaction for safety",
                "recommendations": ["Manual review required", "System check needed"],
                "reason": f"Only {len(completed_analyzers)} of minimum {config.min_analyzers_required} analyzers completed"
            }
        else:
            # Get the decision aggregator LLM instance
            node_instance = _get_node_instance("decision_aggregator", "llm")

            # Prepare input for the aggregator with all analyzer texts
            processing_input = {
                "transaction": transaction,
                "analyzer_reports": analyzer_summaries,
                "analyzers_completed": completed_analyzers,
                "instruction": "Based on all the analyzer reports, provide a final fraud decision"
            }

            # The aggregator LLM will return structured JSON using schema
            # The prompt should be configured to request JSON with: final_decision, conclusion, recommendations, reason
            result = await node_instance.run(json.dumps(processing_input))

            # Parse the JSON response from the aggregator
            try:
                if isinstance(result, str):
                    final_output = json.loads(result)
                else:
                    final_output = result

                # Ensure required fields exist
                if "final_decision" not in final_output:
                    final_output["final_decision"] = "DECLINE"
                if "conclusion" not in final_output:
                    final_output["conclusion"] = "Unable to determine - declining for safety"
                if "recommendations" not in final_output:
                    final_output["recommendations"] = []
                if "reason" not in final_output:
                    final_output["reason"] = "Analysis completed"

            except json.JSONDecodeError:
                # If JSON parsing fails, create a default response
                final_output = {
                    "final_decision": "DECLINE",
                    "conclusion": "Error processing analyzer results",
                    "recommendations": ["Manual review required"],
                    "reason": str(result)[:500] if result else "No response from aggregator"
                }

        # Update state with final decision output
        state["final_decision"] = final_output["final_decision"]
        state["final_output"] = final_output
        state = set_stage_result(state, "decision_aggregator", final_output)

        # Add AI message
        message = AIMessage(content=f"Decision Aggregator: {final_output['final_decision']} - {final_output['conclusion']}")
        state = add_message(state, message)
        
        return state
        
    except Exception as e:
        error_msg = f"DecisionAggregator node error: {str(e)}"
        print(f"❌ {error_msg}")
        return set_error(state, error_msg)

async def finalizer_node(state: AgentState) -> AgentState:
    """
    Finalizer node that merges results from parallel execution.
    
    This node consolidates all results from parallel branches and prepares
    the final output for the agent. It's automatically included in all agents
    to enable parallelization and data merging.
    
    Args:
        state: Current agent state with results from all parallel nodes
        
    Returns:
        Updated state with merged final results
    """
    try:
        from datetime import datetime
        from langchain_core.messages import AIMessage
        
        # Get all results from parallel execution
        all_results = state.get("results", {})
        
        # Merge all results into a final output
        final_output = {
            "merged_results": all_results,
            "execution_summary": {
                "total_stages": len(all_results),
                "completed_stages": list(all_results.keys()),
                "finalization_timestamp": datetime.now().isoformat()
            }
        }
        
        # Create new state without circular references
        updated_results = dict(state.get("results", {}))
        updated_results["finalizer"] = final_output
        
        updated_messages = list(state.get("messages", []))
        final_message = AIMessage(content=f"Finalizer: Merged results from {len(all_results)} parallel stages")
        updated_messages.append(final_message)
        
        # Return new state with proper structure
        return {
            "input": state.get("input"),
            "messages": updated_messages,
            "context": state.get("context", {}),
            "results": updated_results,
            "current_stage": "finalizer",
            "error": state.get("error"),
            "metadata": state.get("metadata", {})
        }
        
    except Exception as e:
        # Handle finalizer errors gracefully
        return {
            "input": state.get("input"),
            "messages": state.get("messages", []),
            "context": state.get("context", {}),
            "results": state.get("results", {}),
            "current_stage": "finalizer",
            "error": f"Finalizer error: {str(e)}",
            "metadata": state.get("metadata", {})
        }

def get_graph_nodes(config: Config) -> Dict[str, Callable]:
    """
    Get graph nodes based on configuration.
    Dynamically returns nodes based on user's LLM and tool node configuration.
    Always includes a finalizer node for parallel execution and data merging.
    
    Args:
        config: Configuration object
        
    Returns:
        Dictionary of node functions including finalizer
    """
    node_functions = {}

    # Add control nodes
    node_functions["orchestrator"] = orchestrator_node

    # Add LLM analyzer nodes
    node_functions["pattern_detector"] = pattern_detector_node
    node_functions["behavioral_analizer"] = behavioral_analizer_node
    node_functions["velocity_checker"] = velocity_checker_node
    node_functions["merchant_risk_analizer"] = merchant_risk_analizer_node
    node_functions["geographic_analizer"] = geographic_analizer_node

    # Add aggregation node
    node_functions["decision_aggregator"] = decision_aggregator_node

    # Always add finalizer node for parallel execution and data merging
    node_functions["finalizer"] = finalizer_node
    
    # Return all nodes including finalizer
    return node_functions

def create_custom_node(stage_name: str, logic_func: Callable) -> Callable:
    """
    Create a custom node function.
    
    Args:
        stage_name: Name of the stage
        logic_func: Logic function for the node
        
    Returns:
        Node function
    """
    async def custom_node(state: AgentState) -> AgentState:
        try:
            clear_error(state)
            result = await logic_func(state)
            state = set_stage_result(state, stage_name, result)
            return state
        except Exception as e:
            return set_error(state, f"{stage_name} error: {str(e)}")
    
    return custom_node
