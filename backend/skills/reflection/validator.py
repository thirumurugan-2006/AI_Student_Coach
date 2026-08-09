"""
Reflection Skill Output Validator.

Validates that the LLM response for the Reflection Skill
conforms to the ReflectionOutputSchema.
"""

from typing import Any

from pydantic import ValidationError
from skills.reflection.schema import ReflectionOutputSchema
from core.logger import logger


class ReflectionValidator:
    """
    Validates structured output from the Reflection Skill.
    """

    @staticmethod
    def validate(data: Any) -> ReflectionOutputSchema:
        """
        Validate raw data against the ReflectionOutputSchema.

        Args:
            data: Raw data from the LLM — dict or JSON string.

        Returns:
            A validated ReflectionOutputSchema instance.

        Raises:
            ValueError: If validation fails.
        """
        try:
            if isinstance(data, ReflectionOutputSchema):
                return data
            if isinstance(data, dict):
                return ReflectionOutputSchema(**data)
            if isinstance(data, str):
                return ReflectionOutputSchema.model_validate_json(data)
            return ReflectionOutputSchema.model_validate(data)
        except ValidationError as e:
            logger.error(f"Reflection output validation failed: {e}")
            raise ValueError(f"Reflection output validation failed: {e}") from e

    @staticmethod
    def is_valid(data: Any) -> bool:
        """Check validity without raising."""
        try:
            ReflectionValidator.validate(data)
            return True
        except ValueError:
            return False
