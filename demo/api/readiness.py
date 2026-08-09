"""
Readiness API Service for Streamlit Demo Frontend.
"""

from api.client import client
from config import API_ENDPOINTS


class ReadinessService:
    """Service for readiness gate API calls."""
    
    def evaluate_readiness(self, user_id: str, access_token: str = None) -> dict:
        """
        Evaluate placement readiness.
        
        Args:
            user_id: The user's ID
            access_token: Optional access token for authentication
            
        Returns:
            Readiness evaluation results
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        return client.post(
            API_ENDPOINTS["readiness"],
            data={"user_id": user_id},
            headers=headers
        )


# Global service instance
readiness_service = ReadinessService()
