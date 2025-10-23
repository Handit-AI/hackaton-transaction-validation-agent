"""
OpenAI client utility for LLM calls with JSON schema support
"""

import os
import json
import aiohttp
import traceback
from typing import Dict, Any, Optional, Union, Type
from openai import AsyncOpenAI
from pydantic import BaseModel


class OpenAIClient:
    """Utility class for OpenAI API calls with JSON schema support"""

    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY_HACKATON")
        if not api_key:
            raise ValueError("OPENAI_API_KEY_HACKATON environment variable not set")

        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = os.getenv("MODEL_NAME_HACKATON", "gpt-4o-mini")
        self.context_url = os.getenv("CONTEXT_API_URL", "https://self-improving-engine-api-299768392189.us-central1.run.app/api/v1/context")
        self.trace_url = os.getenv("TRACE_API_URL", "https://self-improving-engine-api-299768392189.us-central1.run.app/api/v1/trace")
    
    async def _get_context(self, input_text: str, node_name: str) -> Dict[str, Any]:
        """
        Get context from the self-improving engine
        
        Args:
            input_text: Input text for the transaction
            node_name: Name of the node making the call
            
        Returns:
            Dictionary with 'context' (full/online), 'bullet_ids', and 'pattern_id'
        """
        try:
            payload = {
                "input_text": input_text,
                "node": node_name,
                "max_bullets_per_evaluator": 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.context_url, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "context": result.get("context", {"full": "", "online": ""}),
                            "bullet_ids": result.get("bullet_ids", {"full": [], "online": []}),
                            "pattern_id": result.get("pattern_id")
                        }
                    else:
                        print(f"⚠️ Context API call failed with status {response.status}")
                        error_text = await response.text()
                        print(f"Error response: {error_text}")
                        print(f"URL: {self.context_url}")
                        print(f"Payload: {payload}")
                        return {
                            "context": {"full": "", "online": ""},
                            "bullet_ids": {"full": [], "online": []},
                            "pattern_id": None
                        }
        except Exception as e:
            print(f"⚠️ Failed to get context: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"URL: {self.context_url}")
            return {
                "context": {"full": "", "online": ""},
                "bullet_ids": {"full": [], "online": []},
                "pattern_id": None
            }
    
    async def _trace_transaction(self, input_text: str, node_name: str, output: Any, ground_truth: Optional[str] = None, agent_reasoning: Optional[str] = None, bullet_ids: Optional[Dict[str, list]] = None, session_id: Optional[str] = None, run_id: Optional[str] = None, model_type: Optional[str] = None):
        """
        Trace transaction to the self-improving engine
        
        Args:
            input_text: Input text for the transaction
            node_name: Name of the node making the call
            output: Output from the LLM
            ground_truth: Optional ground truth (defaults to output)
            agent_reasoning: Optional agent's reasoning
            bullet_ids: Optional bullet IDs from context endpoint
            session_id: Optional session ID for tracking multiple runs
            run_id: Optional run ID within session
            model_type: Optional model type (vanilla, full, online)
        """
        try:
            # Convert output to string if it's not already
            output_str = json.dumps(output) if isinstance(output, (dict, list)) else str(output)
            
            payload = {
                "input_text": input_text,
                "node": node_name,
                "output": output_str,
                "ground_truth": ground_truth if ground_truth else output_str,
                "agent_reasoning": agent_reasoning if agent_reasoning else ""
            }
            
            # Add bullet_ids if provided
            if bullet_ids:
                payload["bullet_ids"] = bullet_ids
            
            # Add session_id if provided
            if session_id is not None:
                payload["session_id"] = session_id
            
            # Add run_id if provided
            if run_id is not None:
                payload["run_id"] = run_id
            
            # Add model_type if provided
            if model_type is not None:
                payload["model_type"] = model_type
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.trace_url, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        print(f"✅ Traced transaction for node: {node_name}")
                        return result  # Return the full response including generated_bullets
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Trace API call failed with status {response.status}")
                        print(f"Error response: {error_text}")
                        print(f"URL: {self.trace_url}")
                        print(f"Payload: {payload}")
                        return None
        except Exception as e:
            print(f"⚠️ Failed to trace transaction: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"URL: {self.trace_url}")
            print(f"Payload: {payload}")
            return None
    
    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        response_format: Optional[Union[Type[BaseModel], Dict[str, Any]]] = None,
        node_name: Optional[str] = None,
        context: Optional[str] = None,
        model_type: str = "vanilla",
        session_id: Optional[str] = None,
        run_id: Optional[str] = None  # Added run_id parameter
    ) -> Union[str, BaseModel]:
        """
        Call OpenAI API with optional JSON schema support.

        Args:
            system_prompt: System message for the LLM (can contain {context} placeholder)
            user_prompt: User message/input
            model: Model name (defaults to env variable)
            temperature: Temperature for sampling
            response_format: Optional Pydantic model or JSON schema for structured output
            node_name: Name of the node making the call (for tracing)
            context: Optional context string to inject into system prompt (replaces {context} placeholder)
            model_type: Type of model execution ("vanilla", "full", or "online") - default is "vanilla"
            session_id: Optional session ID for tracking multiple runs
            run_id: Optional run ID within session

        Returns:
            String response or parsed Pydantic model instance
        """
        model_name = model or self.default_model
        
        # Get context based on model_type
        actual_context = context if context else ""
        bullet_ids = None
        
        if model_type in ["full", "online"] and node_name:
            # Fetch context from API
            context_data = await self._get_context(user_prompt, node_name)
            print(f"Context data: {context_data}")
            if model_type == "full":
                actual_context = context_data.get("context", {}).get("full", "")
                bullet_ids = context_data.get("bullet_ids", {"full": [], "online": []})
            elif model_type == "online":
                actual_context = context_data.get("context", {}).get("online", "")
                bullet_ids = context_data.get("bullet_ids", {"full": [], "online": []})
        
        # Replace {context} placeholder in system prompt with actual context
        # Replace both {context} and {CONTEXT} placeholders
        formatted_system_prompt = system_prompt.replace("{context}", actual_context).replace("{CONTEXT}", actual_context)
        
        # Store original for tracing
        original_system_prompt = system_prompt

        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Prepare kwargs for the API call
        kwargs = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }

        # Add response format if specified
        if response_format:
            if isinstance(response_format, type) and issubclass(response_format, BaseModel):
                # Use Pydantic model for structured output
                kwargs["response_format"] = response_format

                # Make the API call with structured output
                response = await self.client.beta.chat.completions.parse(
                    **kwargs
                )

                # Return the parsed object
                result = response.choices[0].message.parsed
                
                # Trace the transaction if node_name is provided
                if node_name:
                    # Combine system and user prompts for input_text
                    combined_input = f"System Prompt:\n{formatted_system_prompt}\n\nUser Prompt:\n{user_prompt}"
                    trace_response = await self._trace_transaction(combined_input, node_name, result, bullet_ids=bullet_ids, session_id=session_id, run_id=run_id, model_type=model_type)
                    if trace_response and "generated_bullets" in trace_response:
                        add_generated_bullets(node_name, trace_response["generated_bullets"])
                
                return result
            else:
                # Use dictionary JSON schema
                kwargs["response_format"] = {"type": "json_object"}

                # Make the API call
                response = await self.client.chat.completions.create(
                    **kwargs
                )

                # Parse and return JSON
                content = response.choices[0].message.content
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    result = content
                
                # Trace the transaction if node_name is provided
                if node_name:
                    # Combine system and user prompts for input_text
                    combined_input = f"System Prompt:\n{formatted_system_prompt}\n\nUser Prompt:\n{user_prompt}"
                    trace_response = await self._trace_transaction(combined_input, node_name, result, bullet_ids=bullet_ids, session_id=session_id, run_id=run_id, model_type=model_type)
                    if trace_response and "generated_bullets" in trace_response:
                        add_generated_bullets(node_name, trace_response["generated_bullets"])
                
                return result
        else:
            # Regular text response
            response = await self.client.chat.completions.create(
                **kwargs
            )

            result = response.choices[0].message.content
            
            # Trace the transaction if node_name is provided
            if node_name:
                # Combine system and user prompts for input_text
                combined_input = f"System Prompt:\n{formatted_system_prompt}\n\nUser Prompt:\n{user_prompt}"
                trace_response = await self._trace_transaction(combined_input, node_name, result, bullet_ids=bullet_ids, session_id=session_id, run_id=run_id, model_type=model_type)
                if trace_response and "generated_bullets" in trace_response:
                    add_generated_bullets(node_name, trace_response["generated_bullets"])
            
            return result



# Global client instance
_client = None

# Global tracker for generated bullets
_generated_bullets = {}

def get_openai_client() -> OpenAIClient:
    """Get or create OpenAI client singleton"""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client

def get_generated_bullets() -> Dict[str, Any]:
    """Get generated bullets tracker"""
    global _generated_bullets
    return _generated_bullets

def clear_generated_bullets():
    """Clear generated bullets tracker"""
    global _generated_bullets
    _generated_bullets = {}

def add_generated_bullets(node_name: str, bullets: Any):
    """Add generated bullets for a node"""
    global _generated_bullets
    if node_name and bullets:
        _generated_bullets[node_name] = bullets