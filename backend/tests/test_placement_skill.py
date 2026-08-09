"""
Tests for Placement Skill with mocking to avoid requiring real LLM calls.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from skills.placement.skill import PlacementSkill
from skills.placement.schema import PlacementOutput
from memory.student_memory import StudentMemory
from core.llm_interface import LLMInterface


@pytest.fixture
def mock_llm():
    """Create a mock LLM interface."""
    llm = Mock(spec=LLMInterface)
    llm.generate = AsyncMock()
    return llm


@pytest.fixture
def mock_memory():
    """Create a mock student memory."""
    memory = Mock(spec=StudentMemory)
    memory.get_profile_summary = Mock(return_value="Test student profile")
    return memory


@pytest.fixture
def placement_skill(mock_llm, mock_memory):
    """Create a PlacementSkill instance with mocked dependencies."""
    skill = PlacementSkill(llm=mock_llm, memory=mock_memory, student_id="test_student")
    return skill


@pytest.mark.asyncio
async def test_placement_skill_execute(placement_skill, mock_llm):
    """Test Placement skill execution with mocked LLM response."""
    # Mock the LLM response
    mock_response = PlacementOutput(
        status="in_progress",
        profile={
            "target_role": "Software Engineer",
            "target_companies": ["Google", "Microsoft"],
            "technical_readiness": 75.0,
            "communication_score": 80.0,
            "interview_readiness": 70.0,
            "resume_quality": 85.0
        },
        recommendations=["Practice DSA", "Improve communication"],
        next_steps=["Solve 5 LeetCode problems", "Join mock interview"],
        estimated_timeline="2-3 months",
        confidence=0.85
    )
    mock_llm.generate.return_value = mock_response
    
    # Execute the skill
    context = {"target_role": "Software Engineer"}
    result = await placement_skill.execute(context=context, schema=PlacementOutput)
    
    # Verify the result
    assert isinstance(result, PlacementOutput)
    assert result.status == "in_progress"
    assert result.profile["target_role"] == "Software Engineer"
    assert len(result.recommendations) == 2
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_placement_skill_with_custom_schema(placement_skill, mock_llm):
    """Test Placement skill with custom schema."""
    mock_response = PlacementOutput(
        status="ready",
        profile={
            "target_role": "Data Scientist",
            "target_companies": ["OpenAI"],
            "technical_readiness": 90.0,
            "communication_score": 85.0,
            "interview_readiness": 88.0,
            "resume_quality": 92.0
        },
        recommendations=["Apply to OpenAI"],
        next_steps=["Submit application"],
        estimated_timeline="1-2 months",
        confidence=0.9
    )
    mock_llm.generate.return_value = mock_response
    
    result = await placement_skill.execute(context={}, schema=PlacementOutput)
    
    assert result.status == "ready"
    assert result.confidence == 0.9
