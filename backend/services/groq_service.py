"""
Groq Service

Reusable asynchronous Groq client for LLM inference.
Handles chat completion, JSON output, structured output validation,
timeout handling, error handling, and logging.
"""

import json
import httpx
import time
from typing import Any, Optional
from pydantic import BaseModel
from config.settings import get_settings
from core.validator import OutputValidator
from core.logger import logger
from core.retry import RetryHandler
from core.constants import MAX_RETRIES, RETRY_BASE_DELAY, RETRY_MAX_DELAY

settings = get_settings()


class GroqService:
    """
    Groq-powered LLM Service.
    Provides a clean interface for interacting with Groq-hosted models.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.timeout = settings.GROQ_TIMEOUT
        self.temperature = settings.GROQ_TEMPERATURE
        self.top_p = settings.GROQ_TOP_P
        self.max_tokens = settings.GROQ_MAX_TOKENS

        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

        # Validate API key
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Please set GROQ_API_KEY in backend/.env file. "
                "Get a free API key at https://console.groq.com/keys"
            )

    @RetryHandler.with_retries(max_retries=MAX_RETRIES, base_delay=RETRY_BASE_DELAY, max_delay=RETRY_MAX_DELAY)
    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False
    ) -> BaseModel | str:
        """
        Generate a response from the Groq model.

        Args:
            prompt: The full text prompt with context and instructions.
            schema: Optional Pydantic model class for structured JSON output.
            stream: Whether to stream the response (future-ready).

        Returns:
            A string response if schema is None, otherwise a validated instance of the schema.

        Raises:
            Exception: for network errors, model errors, or validation failures.
        """
        start_time = time.time()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": stream,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }

        if schema:
            payload["response_format"] = {"type": "json_object"}

        logger.info(f"Sending request to Groq ({self.model})")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()

            except httpx.ConnectError as e:
                logger.error(f"Failed to connect to Groq API.")
                raise ConnectionError(f"Groq API not reachable: {e}") from e
            except httpx.TimeoutException as e:
                logger.error(f"Groq request timed out after {self.timeout}s.")
                raise TimeoutError(f"Groq request timed out: {e}") from e
            except httpx.HTTPStatusError as e:
                error_msg = response.text if response else str(e)
                logger.error(f"Groq returned HTTP error {e.response.status_code}: {error_msg}")
                raise RuntimeError(f"Groq HTTP Error: {error_msg}") from e

        elapsed = time.time() - start_time
        logger.info(f"Groq response received in {elapsed:.2f}s")

        data = response.json()

        try:
            message = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Groq response format. Keys: {list(data.keys())}")
            raise ValueError(f"Invalid Groq response format: {e}") from e

        logger.debug(f"Extracted message length: {len(message)} characters")

        if not message:
            logger.error("Empty response detected from Groq.")
            raise ValueError("Groq returned an empty response.")

        if not schema:
            return message

        try:
            parsed_json = json.loads(message)
            validated_obj = await OutputValidator.validate_schema_async(parsed_json, schema)
            
            # Ensure the validated object is not a coroutine
            if hasattr(validated_obj, '__await__'):
                logger.warning("Validated object is still a coroutine after validation, awaiting it...")
                validated_obj = await validated_obj
            
            # Final check - if still a coroutine, this is a critical error
            if hasattr(validated_obj, '__await__'):
                logger.error(f"CRITICAL: Validated object is still a coroutine after double-await. Type: {type(validated_obj)}")
                raise RuntimeError("Validation returned a coroutine instead of a Pydantic model")
            
            return validated_obj

        except json.JSONDecodeError as e:
            logger.error(f"Groq did not return valid JSON: {message[:200]}")
            raise ValueError(f"Invalid JSON received from Groq: {e}") from e
        except ValueError as e:
            logger.error(f"Pydantic schema validation failed: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the Groq API is accessible.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                logger.info("Groq API health check passed")
                return True
        except Exception as e:
            logger.error(f"Groq API health check failed: {e}")
            return False
