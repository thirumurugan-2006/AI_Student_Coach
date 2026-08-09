"""
Workflow API Service for Streamlit Demo Frontend.
Communicates with the Workflow Controller.
"""

from api.client import client
from config import API_ENDPOINTS


class WorkflowService:
    """Service for workflow state API calls."""
    
    def get_workflow_state(self, user_id: str, access_token: str = None) -> dict:
        """
        Get current workflow state from backend.
        
        Args:
            user_id: The user's ID
            access_token: Optional access token for authentication
            
        Returns:
            Workflow state including current_module, current_skill, next_action, progress
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        return client.get(
            API_ENDPOINTS["workflow"],
            params={"user_id": user_id},
            headers=headers
        )
    
    def submit_skill_result(self, user_id: str, skill: str, result: dict, access_token: str = None) -> dict:
        """
        Submit skill result to backend for evaluation and next action.
        
        Args:
            user_id: The user's ID
            skill: The skill that was completed
            result: The result data from the skill
            access_token: Optional access token for authentication
            
        Returns:
            Evaluation result and next action from backend
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        return client.post(
            API_ENDPOINTS["workflow"],
            data={
                "user_id": user_id,
                "skill": skill,
                "result": result
            },
            headers=headers
        )


# Global service instance
workflow_service = WorkflowService()
