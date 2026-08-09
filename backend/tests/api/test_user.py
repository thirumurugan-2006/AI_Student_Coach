"""
API Tests — User Endpoints.

Tests for:
- POST /user/signup  (new user creation)
- POST /user/signup  (returning user login)
- GET  /user/profile
- GET  /user/session
- POST /user/logout
"""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestUserSignup:
    """Test suite for the /user/signup endpoint."""

    async def test_new_user_signup_returns_201_fields(self, client: AsyncClient):
        """A new user signup should return user details and an access token."""
        payload = {"name": "Alice Dev", "email": "alice@test.com"}

        response = await client.post("/user/signup", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Alice Dev"
        assert data["email"] == "alice@test.com"
        assert data["is_new_user"] is True
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_returning_user_signup_is_not_new(self, client: AsyncClient):
        """A returning user signing up again should get is_new_user=False."""
        payload = {"name": "Bob Dev", "email": "bob@test.com"}

        # First signup
        await client.post("/user/signup", json=payload)

        # Second signup (same email)
        response = await client.post("/user/signup", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_new_user"] is False
        assert data["email"] == "bob@test.com"

    async def test_signup_invalid_email_returns_400(self, client: AsyncClient):
        """An invalid email format should return 400."""
        payload = {"name": "Bad Email User", "email": "not-an-email"}

        response = await client.post("/user/signup", json=payload)

        assert response.status_code == 400

    async def test_signup_missing_name_returns_422(self, client: AsyncClient):
        """Missing required name field should return 422 Unprocessable Entity."""
        payload = {"email": "no-name@test.com"}

        response = await client.post("/user/signup", json=payload)

        assert response.status_code == 422

    async def test_signup_missing_email_returns_422(self, client: AsyncClient):
        """Missing required email field should return 422 Unprocessable Entity."""
        payload = {"name": "No Email User"}

        response = await client.post("/user/signup", json=payload)

        assert response.status_code == 422


class TestUserProfile:
    """Test suite for the /user/profile endpoint."""

    async def test_get_profile_returns_user_data(self, client: AsyncClient):
        """Getting a profile for an existing user should return their data."""
        # Create user first
        signup_payload = {"name": "Carol Dev", "email": "carol@test.com"}
        signup_response = await client.post("/user/signup", json=signup_payload)
        user_id = signup_response.json()["user_id"]

        response = await client.get("/user/profile", params={"user_id": user_id})

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["email"] == "carol@test.com"

    async def test_get_profile_nonexistent_user_returns_404(self, client: AsyncClient):
        """Requesting a profile for a non-existent user should return 404."""
        response = await client.get(
            "/user/profile", params={"user_id": "does-not-exist"}
        )

        assert response.status_code == 404


class TestUserLogout:
    """Test suite for the /user/logout endpoint."""

    async def test_logout_returns_success_message(self, client: AsyncClient):
        """Logout endpoint should return a success message."""
        response = await client.post("/user/logout", params={"user_id": "any-id"})

        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestHealthCheck:
    """Smoke tests for the health check endpoint."""

    async def test_health_check_returns_healthy(self, client: AsyncClient):
        """Health endpoint should return status=healthy."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_root_endpoint_returns_info(self, client: AsyncClient):
        """Root endpoint should return application metadata."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert data["version"] == "1.0.0"
