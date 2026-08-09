"""
Learning Skill Output Validator.

Validates that the LLM response for the Learning Skill
conforms to the LearningOutputSchema.
"""

from typing import Any

from pydantic import ValidationError
from skills.learning.schema import LearningOutputSchema
from core.logger import logger


class LearningValidator:
    """
    Validates structured output from the Learning Skill.
    """

    @staticmethod
    def validate(data: Any) -> LearningOutputSchema:
        """
        Validate raw data against the LearningOutputSchema.

        Args:
            data: Raw data from the LLM — dict or JSON string.

        Returns:
            A validated LearningOutputSchema instance.

        Raises:
            ValueError: If validation fails.
        """
        try:
            if isinstance(data, LearningOutputSchema):
                return data
            if isinstance(data, dict):
                return LearningOutputSchema(**data)
            if isinstance(data, str):
                return LearningOutputSchema.model_validate_json(data)
            return LearningOutputSchema.model_validate(data)
        except ValidationError as e:
            logger.error(f"Learning output validation failed: {e}")
            raise ValueError(f"Learning output validation failed: {e}") from e

    @staticmethod
    def is_valid(data: Any) -> bool:
        """Check validity without raising."""
        try:
            LearningValidator.validate(data)
            return True
        except ValueError:
            return False
