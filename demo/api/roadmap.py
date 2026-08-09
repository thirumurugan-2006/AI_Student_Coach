"""
Roadmap API Service for Streamlit Demo Frontend.
"""

from api.client import client
from config import API_ENDPOINTS


class RoadmapService:
    """Service for learning roadmap API calls."""
    
    def generate_roadmap(self, user_id: str, topic_request: str, access_token: str = None) -> dict:
        """
        Generate a personalized learning roadmap.
        
        Args:
            user_id: The user's ID
            topic_request: The topic to create a roadmap for
            access_token: Optional access token for authentication
            
        Returns:
            Learning roadmap results
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        return client.post(
            API_ENDPOINTS["roadmap"],
            data={"user_id": user_id, "topic_request": topic_request},
            headers=headers
        )


# Global service instance
roadmap_service = RoadmapService()
