from typing import Any, Optional
from pydantic import BaseModel
from config.settings import get_settings

from services.groq_service import GroqService
from services.ollama_service import OllamaService
from core.logger import logger

settings = get_settings()


class ContentLLM:
    """
    Content Generation LLM Interface using Groq.
    Used for generating structured content like MCQs, assessments, learning materials.
    """

    def __init__(self):
        self.groq = GroqService()
        logger.info("ContentLLM: Initialized with Groq provider")

    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False
    ) -> BaseModel | str:
        """
        Generate content using Groq.

        Args:
            prompt: The full text prompt with context and instructions.
            schema: Optional Pydantic model class for structured JSON output.
            stream: Whether to stream the response.

        Returns:
            A string response if schema is None, otherwise a validated instance of the schema.
        """
        logger.info("ContentLLM: Generating via Groq")
        result = await self.groq.generate(prompt=prompt, schema=schema, stream=stream)
        return result

    async def health_check(self) -> bool:
        """Check if Groq is healthy."""
        return await self.groq.health_check()


class PlanningLLM:
    """
    Planning/Reasoning LLM Interface using Ollama (Qwen3 4B).
    Used for workflow planning, next-action reasoning, and decision support.
    """

    def __init__(self):
        try:
            self.ollama = OllamaService()
            logger.info("PlanningLLM: Initialized with Ollama provider")
        except ValueError as e:
            logger.warning(f"PlanningLLM: {e}")
            self.ollama = None

    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False
    ) -> BaseModel | str:
        """
        Generate planning/reasoning using Ollama.

        Args:
            prompt: The full text prompt with context and instructions.
            schema: Optional Pydantic model class for structured JSON output.
            stream: Whether to stream the response.

        Returns:
            A string response if schema is None, otherwise a validated instance of the schema.

        Raises:
            Exception: if Ollama is not configured or fails.
        """
        if not self.ollama:
            raise Exception(
                "PlanningLLM is not available. "
                "Ollama must be configured with Qwen3 4B for planning/reasoning tasks. "
                "Set OLLAMA_HOST and OLLAMA_MODEL in backend/.env"
            )

        logger.info("PlanningLLM: Generating via Ollama")
        result = await self.ollama.generate(prompt=prompt, schema=schema, stream=stream)
        return result

    async def health_check(self) -> bool:
        """Check if Ollama is healthy."""
        if not self.ollama:
            return False
        return await self.ollama.health_check()


class LLMInterface:
    """
    Unified LLM Interface that provides both content generation and planning capabilities.
    Maintains backward compatibility while supporting the two-model architecture.
    """

    def __init__(self):
        # Determine provider from settings; default is 'groq'
        self.provider = settings.LLM_PROVIDER
        # Defer creation of LLM service instances until actually needed to avoid initialization errors (e.g., missing API keys)
        self.content: ContentLLM | None = None
        self.planning: PlanningLLM | None = None
        logger.info(f"LLM Interface: Initialized with provider '{self.provider}'.")

    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False,
        use_planning: bool = False
    ) -> BaseModel | str:
        """
        Generate a response using the appropriate LLM.

        Args:
            prompt: The full text prompt with context and instructions.
            schema: Optional Pydantic model class for structured JSON output.
            stream: Whether to stream the response.
            use_planning: If True, use PlanningLLM (Ollama), otherwise use ContentLLM (Groq).

        Returns:
            A string response if schema is None, otherwise a validated instance of the schema.
        """
        # Lazy initialization of the required LLM based on provider or explicit flag
        if use_planning or self.provider == "ollama":
            if self.planning is None:
                self.planning = PlanningLLM()
            return await self.planning.generate(prompt=prompt, schema=schema, stream=stream)
        else:
            if self.content is None:
                self.content = ContentLLM()
            return await self.content.generate(prompt=prompt, schema=schema, stream=stream)

    async def health_check(self) -> bool:
        """Check health of the selected LLM provider.

        Returns:
            True if the selected provider reports healthy, False otherwise.
        """
        if self.provider == "ollama":
            if self.planning is None:
                self.planning = PlanningLLM()
            return await self.planning.health_check()
        else:
            if self.content is None:
                self.content = ContentLLM()
            return await self.content.health_check()

