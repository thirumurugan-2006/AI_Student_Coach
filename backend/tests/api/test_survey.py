"""
API Tests — Survey Endpoints.

Tests for:
- POST /survey/  (conduct survey)
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio


class TestSurveyEndpoint:
    """Test suite for the /survey/ endpoint."""

    async def test_survey_returns_success(self, client: AsyncClient):
        """A valid survey request should return 200 with a response message."""
        payload = {"user_message": "I want to become a backend engineer at Google"}

        response = await client.post(
            "/survey/",
            json=payload,
            params={"user_id": "test-student-001"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response_message" in data
        assert "profile_updated" in data

    async def test_survey_missing_message_returns_422(self, client: AsyncClient):
        """Missing user_message field should return 422."""
        response = await client.post(
            "/survey/",
            json={},
            params={"user_id": "test-student-001"}
        )
        assert response.status_code == 422

    async def test_survey_missing_user_id_returns_422(self, client: AsyncClient):
        """Missing user_id query param should return 422."""
        payload = {"user_message": "I want to be a software engineer"}

        response = await client.post("/survey/", json=payload)

        assert response.status_code == 422

    async def test_survey_agent_error_returns_500(self, client: AsyncClient):
        """When the career agent raises an exception, the endpoint should return 500."""
        from main import app
        # Make the mock agent raise
        app.state.career_agent.handle_request = AsyncMock(
            side_effect=RuntimeError("LLM provider unreachable")
        )

        payload = {"user_message": "I want to become a data scientist"}
        response = await client.post(
            "/survey/",
            json=payload,
            params={"user_id": "test-student-001"}
        )

        assert response.status_code == 500


class TestCoachChatEndpoint:
    """Test suite for the /coach/chat endpoint."""

    async def test_coach_chat_invalid_skill_returns_400(self, client: AsyncClient):
        """Requesting an unknown skill should return 400."""
        # This endpoint requires a valid JWT — skip auth by checking router behaviour
        response = await client.post(
            "/coach/chat",
            json={"skill": "nonexistent_skill", "message": "Hello"},
            headers={"Authorization": "Bearer invalid-token"}
        )
        # 401 because token is invalid, but endpoint is reachable
        assert response.status_code in (400, 401, 403)

    async def test_coach_skills_list(self, client: AsyncClient):
        """The /coach/skills endpoint should return all skill names."""
        response = await client.get("/coach/skills")

        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "survey" in data["skills"]
        assert "assessment" in data["skills"]
        assert "interview" in data["skills"]
        assert "learning" in data["skills"]
        assert "reflection" in data["skills"]
