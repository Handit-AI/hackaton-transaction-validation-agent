"""
DecisionAggregator LLM node
"""

import asyncio
from typing import Any, Dict
from pydantic import BaseModel
from src.base import BaseLLMNode, NodeExecutionError
from .prompts import get_prompts


class FraudDecision(BaseModel):
    """Schema for fraud decision output - ensures structured JSON response"""
    final_decision: str  # APPROVE, REVIEW, or DECLINE
    conclusion: str  # Brief summary of the analysis
    recommendations: list[str]  # List of recommended actions
    reason: str  # Detailed explanation of the decision

class DecisionAggregatorLLMNode(BaseLLMNode):
    """
    DecisionAggregator LLM node implementation
    
    This node processes input using LLM capabilities for the decision_aggregator functionality.
    Customize the run() method to implement your specific LLM logic and AI system calls.
    """
    
    def __init__(self, config):
        super().__init__(config, "decision_aggregator")
        # Load node-specific prompts
        self.node_prompts = get_prompts()
    
    async def run(self, input_data: Any) -> Any:
        """
        Execute the decision_aggregator LLM logic with comprehensive error recovery.
        
        Args:
            input_data: Input data to process with LLM
            
        Returns:
            LLM-processed result
            
        Raises:
            NodeExecutionError: If all recovery attempts fail
        """
        max_retries = 3
        retry_delay = 2.0  # Longer delay for LLM calls
        
        for attempt in range(max_retries):
            try:
                # Validate input
                if not self.validate_input(input_data):
                    raise ValueError(f"Invalid input data for {self.node_name}")
                
                # Execute with timeout (longer for LLM calls)
                result = await self._execute_decision_aggregator_llm_logic(input_data)
                print(f"Result in decision_aggregator_llm: {result}")
                # Validate output
                if not self.validate_output(result):
                    raise ValueError(f"Invalid output from {self.node_name}")
                
                return result
                
            except (ValueError, TypeError) as e:
                # Validation errors - don't retry
                print(f"❌ Validation error in {self.node_name}: {e}")
                raise NodeExecutionError(f"Validation failed in {self.node_name}: {e}")
                
            except Exception as e:
                print(f"⚠️ LLM error in {self.node_name} (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt == max_retries - 1:
                    error_msg = f"Failed to execute {self.node_name} after {max_retries} attempts: {e}"
                    print(f"❌ {error_msg}")
                    raise NodeExecutionError(error_msg)
                
                # Exponential backoff with longer delays for LLM
                await asyncio.sleep(retry_delay * (2 ** attempt))
        
        raise NodeExecutionError(f"Unexpected error in {self.node_name} execution")
    
    async def _execute_decision_aggregator_llm_logic(self, data: Any) -> Any:
        """
        Execute the specific decision_aggregator LLM logic with structured JSON output

        This method uses OpenAI's structured output feature to ensure the response
        always conforms to the required JSON schema for fraud decisions.
        """
        # Get the appropriate prompt for this node
        system_prompt = self.node_prompts.get("system", "You are a helpful AI assistant.")
        user_prompt = self.node_prompts.get("user_template", "Process the following input: {input}")

        # Use the new OpenAI utility with structured output
        from src.utils import get_openai_client
        client = get_openai_client()
        
        # Parse JSON string if data is a string
        import json
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse JSON data: {data}")
                data = {"input": data}

        # Format the user prompt with the input data
        formatted_prompt = user_prompt.format(input=str(data))
        
        # Extract context from data if available (optional, can be empty)
        context = data.get("backend_context", "") if isinstance(data, dict) else ""
        
        # Extract session_id, run_id, and model_type from metadata if available
        metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
        session_id = metadata.get("session_id") if isinstance(metadata, dict) else None
        run_id = metadata.get("run_id") if isinstance(metadata, dict) else None
        model_type = metadata.get("model_type", "vanilla") if isinstance(metadata, dict) else "vanilla"

        # Call the LLM with structured output (JSON schema)
        decision = await client.call_llm(
            system_prompt=system_prompt,
            user_prompt=formatted_prompt,
            temperature=self.model_config.get("temperature", 0.2),
            response_format=FraudDecision,  # This ensures structured JSON output
            node_name=self.node_name,
            context=context,  # Pass optional context
            model_type=model_type,  # Pass model_type
            session_id=session_id,  # Pass session_id
            run_id=run_id  # Pass run_id
        )
        # Convert Pydantic model to dictionary for downstream processing
        if hasattr(decision, 'model_dump'):
            return decision.model_dump()
        elif hasattr(decision, 'dict'):
            return decision.dict()
        else:
            # If it's already a dict or string, return as is
            return decision
