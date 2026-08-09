"""
Skill Gap API Service for Streamlit Demo Frontend.
"""

from api.client import client
from config import API_ENDPOINTS


class SkillGapService:
    """Service for skill gap analysis API calls."""
    
    def analyze_skill_gap(self, user_id: str, access_token: str = None) -> dict:
        """
        Analyze skill gaps based on assessment results.
        
        Args:
            user_id: The user's ID
            access_token: Optional access token for authentication
            
        Returns:
            Skill gap analysis results
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        return client.post(
            API_ENDPOINTS["skill_gap"],
            data={"user_id": user_id},
            headers=headers
        )


# Global service instance
skill_gap_service = SkillGapService()
