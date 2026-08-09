"""
Interview API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class InterviewService:
    """Service for interview-related API calls."""
    
    @staticmethod
    def conduct_interview(user_id: str, company_name: str, job_role: str, user_response: str) -> Dict[str, Any]:
        """
        Conduct an interview interaction.
        
        Args:
            user_id: User ID
            company_name: Target company name
            job_role: Target job role
            user_response: User's answer to interview question
            
        Returns:
            Interview response with next question or evaluation
        """
        data = {
            "company_name": company_name,
            "job_role": job_role,
            "user_response": user_response
        }
        params = {"user_id": user_id}
        return client.post(API_ENDPOINTS["interview"], data=data, params=params)


interview_service = InterviewService()
