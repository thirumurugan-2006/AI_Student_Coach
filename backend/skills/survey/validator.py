from pydantic import ValidationError

from .schema import SurveyOutput


class SurveyValidator:
    """Validator for SurveyOutput responses from LLM.

    Provides class methods so it can be used without instantiation, matching test expectations.
    """

    @classmethod
    def validate(cls, response: dict) -> SurveyOutput:
        """Validate raw LLM response against SurveyOutput schema.

        Args:
            response: Dictionary returned by the LLM.

        Returns:
            SurveyOutput: Validated Pydantic model.

        Raises:
            ValueError: If validation fails.
        """
        try:
            validated = SurveyOutput.model_validate(response)
            return validated
        except ValidationError as error:
            raise ValueError(f"Survey validation failed:\n{error}")

    @classmethod
    def is_valid(cls, response: dict) -> bool:
        """Check if a given response dictionary is valid according to SurveyOutput schema.

        Returns True if validation succeeds, False otherwise.
        """
        try:
            cls.validate(response)
            return True
        except Exception:
            return False

    # -----------------------------------------------------

    @classmethod
    def is_complete(cls, survey: SurveyOutput) -> bool:
        """Check whether enough information has been collected."""
        profile = survey.profile
        required = [
            profile.career_goal,
            profile.experience_level,
            profile.primary_language,
            profile.learning_style,
            profile.timeline,
        ]
        return all(required)

    # -----------------------------------------------------

    @classmethod
    def has_missing_fields(cls, survey: SurveyOutput) -> bool:
        return len(survey.missing_information) > 0

    # -----------------------------------------------------

    @classmethod
    def validate_confidence(cls, survey: SurveyOutput) -> bool:
        return survey.confidence >= 0.75