"""
Survey API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class SurveyService:
    """Service for survey-related API calls."""
    
    @staticmethod
    def conduct_survey(user_id: str, user_message: str, access_token: str = None) -> Dict[str, Any]:
        """
        Conduct a survey interaction (fetch next question).
        
        Args:
            user_id: User ID
            user_message: User's response to survey question
            access_token: Optional access token for authentication
            
        Returns:
            Survey response with next question
        """
        data = {"user_message": user_message}
        params = {"user_id": user_id}
        headers = {}
        if access_token and access_token.strip():
            headers["Authorization"] = f"Bearer {access_token}"
        return client.post(API_ENDPOINTS["survey"], data=data, params=params, headers=headers)
    
    @staticmethod
    def conduct_survey_with_answer(user_id: str, answer_data: Dict[str, Any], access_token: str = None) -> Dict[str, Any]:
        """
        Submit a survey answer with question_id.
        
        Args:
            user_id: User ID
            answer_data: Dictionary containing user_message and question_id
            access_token: Optional access token for authentication
            
        Returns:
            Survey response with next question
        """
        data = answer_data
        params = {"user_id": user_id}
        headers = {}
        if access_token and access_token.strip():
            headers["Authorization"] = f"Bearer {access_token}"
        return client.post(API_ENDPOINTS["survey"], data=data, params=params, headers=headers)


survey_service = SurveyService()
