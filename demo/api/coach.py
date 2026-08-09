"""
Career Coach API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any, Optional
from api.client import client, API_ENDPOINTS


class CoachService:
    """Service for career coach-related API calls."""
    
    @staticmethod
    def chat(skill: str, message: str, user_id: str, context: Optional[Dict[str, Any]] = None, access_token: str = None) -> Dict[str, Any]:
        """
        Chat with the Career Coach.
        
        Args:
            skill: Skill to invoke (survey, assessment, learning, interview, reflection)
            message: User's message
            user_id: User ID
            context: Additional context
            access_token: JWT access token
            
        Returns:
            Career Coach response
        """
        data = {
            "skill": skill,
            "message": message,
            "context": context or {}
        }
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        params = {"user_id": user_id}
        return client.post(API_ENDPOINTS["coach_chat"], data=data, params=params, headers=headers)
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        """
        Get Career Coach status.
        
        Returns:
            Career Coach status with registered skills
        """
        return client.get(API_ENDPOINTS["coach_status"])
    
    @staticmethod
    def get_skills() -> Dict[str, Any]:
        """
        Get available skills.
        
        Returns:
            List of available skills
        """
        return client.get(API_ENDPOINTS["coach_skills"])


coach_service = CoachService()
