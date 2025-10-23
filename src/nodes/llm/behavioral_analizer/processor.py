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
        
        Available prompts: {list(self.prompts.keys())}
        Model configuration: {self.model_config}
        """        
        # Get the appropriate prompt for this node
        system_prompt = self.prompts.get("system", "You are a helpful AI assistant.")
        user_prompt = self.prompts.get("user_template", "Process the following input: {input}")
        
        # LLM integration based on configured provider
        model_name = self.model_config.get("name", "gpt-4")
        
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        llm = ChatOpenAI(model=model_name)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt.format(input=str(data)))
        ]
        response = await llm.agenerate([messages])
        return response.generations[0][0].text
