"""
User API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class UserService:
    """Service for user-related API calls."""
    
    @staticmethod
    def signup(name: str, email: str) -> Dict[str, Any]:
        """
        Sign up or login a user.
        
        Args:
            name: User's name
            email: User's email
            
        Returns:
            User session response with access token
        """
        data = {
            "name": name,
            "email": email
        }
        return client.post(API_ENDPOINTS["signup"], data=data)
    
    @staticmethod
    def get_profile(user_id: str) -> Dict[str, Any]:
        """
        Get user profile.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data
        """
        params = {"user_id": user_id}
        return client.get(API_ENDPOINTS["profile"], params=params)
    
    @staticmethod
    def get_session(user_id: str) -> Dict[str, Any]:
        """
        Get user session info.
        
        Args:
            user_id: User ID
            
        Returns:
            User session data
        """
        params = {"user_id": user_id}
        return client.get(API_ENDPOINTS["session"], params=params)
    
    @staticmethod
    def logout(user_id: str) -> Dict[str, Any]:
        """
        Logout user.
        
        Args:
            user_id: User ID
            
        Returns:
            Logout confirmation
        """
        params = {"user_id": user_id}
        return client.post(API_ENDPOINTS["logout"], params=params)


user_service = UserService()
