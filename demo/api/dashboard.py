"""
Dashboard API Service for Streamlit Demo Frontend.
"""

from typing import Dict, Any
from api.client import client, API_ENDPOINTS


class DashboardService:
    """Service for dashboard-related API calls."""
    
    @staticmethod
    def get_dashboard(user_id: str, access_token: str = None) -> Dict[str, Any]:
        """
        Get dashboard data.
        
        Args:
            user_id: User ID
            access_token: JWT access token
            
        Returns:
            Dashboard data with recommendations
        """
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        params = {"user_id": user_id}
        return client.get(API_ENDPOINTS["dashboard"], params=params, headers=headers)


dashboard_service = DashboardService()
