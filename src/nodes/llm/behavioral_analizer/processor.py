"""
BehavioralAnalizer LLM node
"""

import asyncio
from typing import Any, Dict
from src.base import BaseLLMNode, NodeExecutionError
from .prompts import get_prompts

class BehavioralAnalizerLLMNode(BaseLLMNode):
    """
    BehavioralAnalizer LLM node implementation
    
    This node processes input using LLM capabilities for the behavioral_analizer functionality.
    Customize the run() method to implement your specific LLM logic and AI system calls.
    """
    
    def __init__(self, config):
        super().__init__(config, "behavioral_analizer")
        # Load node-specific prompts
        self.node_prompts = get_prompts()
    
    async def run(self, input_data: Any) -> Any:
        """
        Execute the behavioral_analizer LLM logic with comprehensive error recovery.
        
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
                result = await self._execute_behavioral_analizer_llm_logic(input_data)
                print(f"Result in behavioral_analizer_llm: {result}")

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
    
    async def _execute_behavioral_analizer_llm_logic(self, data: Any) -> Any:
        """
        Execute the specific behavioral_analizer LLM logic
        
        This method should call your AI system with the appropriate prompts.
        Customize this method to implement your specific LLM integration:
        
        - OpenAI API calls
        - Ollama local model calls  
        - Anthropic Claude API calls
        - Custom model endpoints
        - Prompt engineering and response processing
        
        Available prompts: {list(self.node_prompts.keys())}
        Model configuration: {self.model_config}
        """        
        # Get the appropriate prompt for this node
        system_prompt = self.node_prompts.get("system", "You are a helpful AI assistant.")
        user_prompt = self.node_prompts.get("user_template", "Process the following input: {input}")

        # Use the new OpenAI utility
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
        
        # Debug: Print raw data
        print(f"🔍 Node processor - Raw data type: {type(data)}")
        print(f"🔍 Node processor - Raw data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        print(f"🔍 Node processor - Raw data: {data}")

        # Format the user prompt with the input data
        formatted_prompt = user_prompt.format(input=str(data))
        
        # Extract context from data if available (optional, can be empty)
        context = data.get("backend_context", "") if isinstance(data, dict) else ""
        
        # Extract session_id, run_id, and model_type from metadata if available
        metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
        print(f"🔍 Node processor - Metadata from data: {metadata}")
        session_id = metadata.get("session_id") if isinstance(metadata, dict) else None
        run_id = metadata.get("run_id") if isinstance(metadata, dict) else None
        model_type = metadata.get("model_type", "vanilla") if isinstance(metadata, dict) else "vanilla"
        
        # Debug logging
        print(f"🔍 Node {self.node_name} - Extracted session_id: {session_id}, run_id: {run_id}, model_type: {model_type}")

        # Call the LLM for text analysis
        response = await client.call_llm(
            system_prompt=system_prompt,
            user_prompt=formatted_prompt,
            temperature=self.model_config.get("temperature", 0.3),
            node_name=self.node_name,
            context=context,  # Pass optional context
            model_type=model_type,  # Pass model_type
            session_id=session_id,  # Pass session_id
            run_id=run_id  # Pass run_id
        )
        return response

