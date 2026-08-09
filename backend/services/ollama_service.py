"""
Ollama Service for Qwen3 4B Planning/Reasoning

Provides a clean interface for interacting with Ollama-hosted models.
Used specifically for planning and reasoning tasks.
"""

import httpx
from typing import Optional
from pydantic import BaseModel
from config.settings import get_settings
from core.logger import logger

settings = get_settings()


class OllamaService:
    """
    Ollama-powered LLM Service for planning and reasoning.
    Uses Qwen3 4B model for intelligent decision support.
    """

    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.endpoint = f"{self.host}/api/generate"

        # Validate configuration
        if not self.host:
            raise ValueError(
                "OLLAMA_HOST is not configured. "
                "Please set OLLAMA_HOST in backend/.env file (e.g., http://localhost:11434)"
            )
        if not self.model:
            raise ValueError(
                "OLLAMA_MODEL is not configured. "
                "Please set OLLAMA_MODEL in backend/.env file (e.g., qwen3:4b)"
            )

        logger.info(f"Ollama Service: Initialized with model {self.model} at {self.host}")

    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False
    ) -> BaseModel | str:
        """
        Generate a response from the Ollama model.

        Args:
            prompt: The full text prompt with context and instructions.
            schema: Optional Pydantic model class for structured JSON output.
            stream: Whether to stream the response (not currently supported).

        Returns:
            A string response if schema is None, otherwise a validated instance of the schema.

        Raises:
            Exception: for network errors, model errors, or validation failures.
        """
        if stream:
            logger.warning("Ollama streaming not yet implemented, using non-streaming")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                result_text = data.get("response", "")
                
                if not result_text:
                    raise ValueError("Ollama returned empty response")

                logger.info(f"Ollama Service: Generated response ({len(result_text)} chars)")

                # If schema is provided, parse and validate
                if schema:
                    import json
                    try:
                        # Try to extract JSON from response
                        json_start = result_text.find("{")
                        json_end = result_text.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = result_text[json_start:json_end]
                            parsed = json.loads(json_str)
                            return schema(**parsed)
                        else:
                            raise ValueError("No valid JSON found in response")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Failed to parse JSON from Ollama response: {e}")

                return result_text

        except httpx.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise Exception(f"Ollama HTTP Error: {e}")
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the Ollama service is healthy.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.host}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                # Check if our model is available
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                if any(self.model in name for name in model_names):
                    logger.info(f"Ollama health check passed: {self.model} available")
                    return True
                else:
                    logger.warning(f"Ollama health check failed: {self.model} not found. Available: {model_names}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
