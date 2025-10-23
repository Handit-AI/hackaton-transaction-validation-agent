"""
OpenAI client utility for LLM calls with JSON schema support
"""

import os
import json
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

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        response_format: Optional[Union[Type[BaseModel], Dict[str, Any]]] = None
    ) -> Union[str, BaseModel]:
        """
        Call OpenAI API with optional JSON schema support.

        Args:
            system_prompt: System message for the LLM
            user_prompt: User message/input
            model: Model name (defaults to env variable)
            temperature: Temperature for sampling
            response_format: Optional Pydantic model or JSON schema for structured output

        Returns:
            String response or parsed Pydantic model instance
        """
        model_name = model or self.default_model

        messages = [
            {"role": "system", "content": system_prompt},
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
                return response.choices[0].message.parsed
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
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        else:
            # Regular text response
            response = await self.client.chat.completions.create(
                **kwargs
            )

            return response.choices[0].message.content



# Global client instance
_client = None

def get_openai_client() -> OpenAIClient:
    """Get or create OpenAI client singleton"""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client