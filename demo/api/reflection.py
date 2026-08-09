"""
Reflection API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class ReflectionService:
    """Service for reflection-related API calls."""
    
    @staticmethod
    def conduct_reflection(user_id: str, reflection_response: str) -> Dict[str, Any]:
        """
        Conduct a reflection interaction.
        
        Args:
            user_id: User ID
            reflection_response: User's reflection response
            
        Returns:
            Reflection response with evaluation
        """
        data = {"reflection_response": reflection_response}
        params = {"user_id": user_id}
        return client.post(API_ENDPOINTS["reflection"], data=data, params=params)


reflection_service = ReflectionService()
