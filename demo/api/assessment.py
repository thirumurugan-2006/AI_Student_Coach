"""
Assessment API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any, Optional
from api.client import client, API_ENDPOINTS


class AssessmentService:
    """Service for assessment-related API calls."""
    
    @staticmethod
    def conduct_assessment(user_id: str, topic: str, answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Conduct an assessment interaction.
        
        Args:
            user_id: User ID
            topic: Assessment topic
            answer: User's answer (optional for initial request)
            
        Returns:
            Assessment response with questions or evaluation
        """
        data = {"topic": topic}
        if answer:
            data["answer"] = answer
        params = {"user_id": user_id}
        return client.post(API_ENDPOINTS["assessment"], data=data, params=params)


assessment_service = AssessmentService()
