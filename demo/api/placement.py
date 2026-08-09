"""
Placement Service for Streamlit Demo Frontend.
Handles API communication for placement assessment functionality.
"""

from typing import Dict, Any, List, Optional
from api.client import client
from config import API_ENDPOINTS


class PlacementService:
    """Service for placement-related API calls."""

    ROUND_ENDPOINTS = {
        "aptitude": API_ENDPOINTS["placement_aptitude"],
        "coding": API_ENDPOINTS["placement_coding"],
        "technical": API_ENDPOINTS["placement_technical"],
        "interview": API_ENDPOINTS["placement_interview"],
        "hr": API_ENDPOINTS["placement_hr"],
        "report": API_ENDPOINTS["placement_report"],
    }

    NEXT_STAGE = {
        "aptitude": "placement_coding",
        "coding": "placement_technical",
        "technical": "placement_interview",
        "interview": "placement_hr",
        "hr": "placement_report",
        "report": "career_intelligence",
    }
    
    @staticmethod
    def assess_placement_readiness(
        user_id: str,
        target_role: Optional[str] = None,
        target_companies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        endpoint = f"{API_ENDPOINTS['placement']}/assess"
        params = {"user_id": user_id}
        data = {
            "target_role": target_role,
            "target_companies": target_companies
        }
        return client.post(endpoint, data=data, params=params)

    @staticmethod
    def get_placement_progress(user_id: str) -> Dict[str, Any]:
        endpoint = f"{API_ENDPOINTS['placement']}/progress"
        params = {"user_id": user_id}
        return client.get(endpoint, params=params)

    def run_round(self, round_name: str, user_id: str, access_token: str = None) -> Dict[str, Any]:
        endpoint = self.ROUND_ENDPOINTS.get(round_name)
        if not endpoint:
            raise ValueError(f"Unknown placement round: {round_name}")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return client.post(f"{endpoint}/", data={}, params={"user_id": user_id}, headers=headers)


placement_service = PlacementService()
