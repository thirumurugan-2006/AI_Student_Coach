"""
Interview Skill Output Validator.

Validates that the LLM response for the Interview Skill
conforms to the InterviewOutputSchema.
"""

from typing import Any

from pydantic import ValidationError
from skills.interview.schema import InterviewOutputSchema
from core.logger import logger


class InterviewValidator:
    """
    Validates structured output from the Interview Skill.
    """

    @staticmethod
    def validate(data: Any) -> InterviewOutputSchema:
        """
        Validate raw data against the InterviewOutputSchema.

        Args:
            data: Raw data from the LLM — dict or JSON string.

        Returns:
            A validated InterviewOutputSchema instance.

        Raises:
            ValueError: If validation fails.
        """
        try:
            if isinstance(data, InterviewOutputSchema):
                return data
            if isinstance(data, dict):
                return InterviewOutputSchema(**data)
            if isinstance(data, str):
                return InterviewOutputSchema.model_validate_json(data)
            return InterviewOutputSchema.model_validate(data)
        except ValidationError as e:
            logger.error(f"Interview output validation failed: {e}")
            raise ValueError(f"Interview output validation failed: {e}") from e

    @staticmethod
    def is_valid(data: Any) -> bool:
        """Check validity without raising."""
        try:
            InterviewValidator.validate(data)
            return True
        except ValueError:
            return False
