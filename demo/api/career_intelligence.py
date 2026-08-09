"""
Career Intelligence API Service for Streamlit Demo Frontend.
"""

from api.client import client
from config import API_ENDPOINTS


class CareerIntelligenceService:
    """Service for career intelligence API calls."""

    def get_intelligence(self, user_id: str, access_token: str = None) -> dict:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return client.get(
            API_ENDPOINTS["career_intelligence"],
            params={"user_id": user_id},
            headers=headers,
        )


career_intelligence_service = CareerIntelligenceService()
