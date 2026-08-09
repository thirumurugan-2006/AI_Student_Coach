"""
Assessment Skill Output Validator.

Validates that the LLM response for the Assessment Skill
conforms to the expected schema before returning to the API layer.
"""

from typing import Any

from pydantic import ValidationError
from skills.assessment.schema import AssessmentOutputSchema
from core.logger import logger


class AssessmentValidator:
    """
    Validates structured output from the Assessment Skill.
    """

    @staticmethod
    def validate(data: Any) -> AssessmentOutputSchema:
        """
        Validate raw data (dict or JSON string) against the AssessmentOutputSchema.

        Args:
            data: Raw data from the LLM — either a dict or JSON string.

        Returns:
            A validated AssessmentOutputSchema instance.

        Raises:
            ValueError: If the data fails schema validation.
        """
        try:
            if isinstance(data, AssessmentOutputSchema):
                return data
            if isinstance(data, dict):
                return AssessmentOutputSchema(**data)
            if isinstance(data, str):
                return AssessmentOutputSchema.model_validate_json(data)
            return AssessmentOutputSchema.model_validate(data)
        except ValidationError as e:
            logger.error(f"Assessment output validation failed: {e}")
            raise ValueError(f"Assessment output validation failed: {e}") from e

    @staticmethod
    def is_valid(data: Any) -> bool:
        """
        Check if data is valid without raising an exception.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            AssessmentValidator.validate(data)
            return True
        except ValueError:
            return False
