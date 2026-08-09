"""
Learning API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class LearningService:
    """Service for learning-related API calls."""
    
    @staticmethod
    def generate_roadmap(user_id: str, topic_request: str, access_token: str = None) -> Dict[str, Any]:
        """
        Generate a learning roadmap.
        
        Args:
            user_id: User ID
            topic_request: Topic to learn about
            access_token: JWT access token
            
        Returns:
            Learning roadmap response
        """
        data = {"topic_request": topic_request}
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return client.post(API_ENDPOINTS["learning"], data=data, headers=headers)


learning_service = LearningService()
