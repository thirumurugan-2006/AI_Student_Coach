"""
Skill Tests — Survey Skill.

Tests for:
- SurveySkill.execute()
- SurveySkill prompt building
- SurveySkill schema validation integration
- SurveySkill validator
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock

from skills.survey.skill import SurveySkill
from skills.survey.schema import SurveyOutput, StudentProfile
from skills.survey.validator import SurveyValidator
from memory.student_memory import StudentMemory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def memory():
    """Fresh StudentMemory with one pre-loaded student."""
    m = StudentMemory()
    m.create_student("s001", "Test Student")
    return m


@pytest.fixture
def mock_llm():
    """Mock LLMInterface."""
    llm = MagicMock()
    llm.generate = AsyncMock()
    return llm


@pytest.fixture
def survey_skill(mock_llm, memory):
    """SurveySkill instance with mock LLM and memory."""
    return SurveySkill(llm=mock_llm, memory=memory)


def _make_survey_output():
    """Return a valid SurveyOutput instance for testing."""
    return SurveyOutput(
        status="complete",
        survey_completed=True,
        profile=StudentProfile(
            career_goal="Backend Engineer",
            target_company="Google",
            experience_level="beginner",
            primary_language="Python",
            known_skills=["Python", "SQL"],
            projects=2,
            study_hours=4,
            learning_style="hands-on",
            weak_topics=["System Design"],
            timeline="3 months",
        ),
        confidence=0.85,
        missing_information=[],
        coach_notification="Survey complete",
    )


# ---------------------------------------------------------------------------
# SurveySkill.execute() Tests
# ---------------------------------------------------------------------------

class TestSurveySkillExecute:

    @pytest.mark.asyncio
    async def test_execute_returns_survey_output(self, survey_skill, mock_llm):
        """execute() should return a SurveyOutput when LLM returns valid JSON."""
        expected = _make_survey_output()
        mock_llm.generate = AsyncMock(return_value=expected)

        context = {"current_message": "I want to become a backend engineer"}
        result = await survey_skill.execute(context=context)

        assert isinstance(result, SurveyOutput)
        assert result.profile.career_goal == "Backend Engineer"
        assert result.survey_completed is True

    @pytest.mark.asyncio
    async def test_execute_calls_llm_with_non_empty_prompt(self, survey_skill, mock_llm):
        """execute() should call LLM Interface with a non-empty prompt."""
        mock_llm.generate = AsyncMock(return_value=_make_survey_output())

        context = {"current_message": "Test message"}
        await survey_skill.execute(context=context)

        # Assert generate was called once
        mock_llm.generate.assert_called_once()
        call_args = mock_llm.generate.call_args
        prompt = call_args[1].get("prompt") or call_args[0][0]
        assert len(prompt) > 10

    @pytest.mark.asyncio
    async def test_execute_uses_survey_output_schema(self, survey_skill, mock_llm):
        """execute() should pass SurveyOutput as the schema to the LLM Interface."""
        mock_llm.generate = AsyncMock(return_value=_make_survey_output())

        context = {"current_message": "Schema test"}
        await survey_skill.execute(context=context)

        call_args = mock_llm.generate.call_args
        # Schema should be SurveyOutput
        schema_arg = call_args[1].get("schema") or (
            call_args[0][1] if len(call_args[0]) > 1 else None
        )
        assert schema_arg is SurveyOutput


# ---------------------------------------------------------------------------
# SurveyValidator Tests
# ---------------------------------------------------------------------------

class TestSurveyValidator:

    def test_validate_valid_dict(self):
        """validate() should accept a valid dictionary and return SurveyOutput."""
        data = {
            "status": "complete",
            "survey_completed": True,
            "profile": {
                "career_goal": "Frontend Engineer",
                "experience_level": "beginner",
                "primary_language": "JavaScript",
                "known_skills": ["React"],
                "projects": 1,
                "study_hours": 3,
                "learning_style": "visual",
                "weak_topics": [],
                "timeline": "6 months",
            },
            "confidence": 0.7,
            "missing_information": [],
        }

        result = SurveyValidator.validate(data)

        assert isinstance(result, SurveyOutput)
        assert result.profile.career_goal == "Frontend Engineer"

    def test_validate_invalid_data_raises_value_error(self):
        """validate() should raise ValueError on invalid data."""
        with pytest.raises(ValueError):
            SurveyValidator.validate({"invalid": "data"})

    def test_is_valid_returns_true_for_valid_data(self):
        """is_valid() should return True for well-formed data."""
        output = _make_survey_output()
        assert SurveyValidator.is_valid(output) is True

    def test_is_valid_returns_false_for_invalid_data(self):
        """is_valid() should return False for malformed data."""
        assert SurveyValidator.is_valid({"garbage": True}) is False


# ---------------------------------------------------------------------------
# StudentMemory Integration
# ---------------------------------------------------------------------------

class TestSurveyMemoryIntegration:

    def test_memory_update_from_survey(self, memory):
        """update_from_survey() should store career goal in memory."""
        profile_data = {
            "career_goal": "Data Engineer",
            "experience_level": "intermediate",
        }

        memory.update_from_survey("s001", profile_data)

        profile = memory.get_profile("s001")
        assert profile["career_goal"] == "Data Engineer"
        assert profile["experience_level"] == "intermediate"
        assert profile["survey_completed"] is True
