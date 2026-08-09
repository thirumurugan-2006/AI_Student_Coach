"""
HTTP Client for Streamlit Demo Frontend.
Handles all API communication with the FastAPI backend.
"""

import requests
import time
from typing import Dict, Any, Optional
from config import API_ENDPOINTS


class APIClient:
    """Base API client for backend communication."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or API_ENDPOINTS["health"].replace("/health", "")
        self.session = requests.Session()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling and timing.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint URL
            data: Request body data
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response JSON data
            
        Raises:
            Exception: If request fails
        """
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                headers=headers,
                timeout=120  # 2 minute timeout for LLM operations
            )
            
            elapsed_time = time.time() - start_time
            
            # Log response time for monitoring
            if elapsed_time > 5:
                print(f"Warning: Request to {endpoint} took {elapsed_time:.2f}s")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {"message": "Success"}
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request to {endpoint} timed out after 120s")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to backend at {endpoint}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication required")
            elif e.response.status_code == 404:
                raise Exception("Resource not found")
            elif e.response.status_code == 422:
                raise Exception(f"Invalid request: {e.response.text}")
            elif e.response.status_code == 500:
                raise Exception(f"Backend error: {e.response.text}")
            else:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params, headers=headers)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data, params=params, headers=headers)
    
    def check_health(self) -> bool:
        """Check if backend is healthy."""
        try:
            response = self.get(API_ENDPOINTS["health"])
            return response.get("status") == "healthy"
        except Exception:
            return False


# Global client instance
client = APIClient()
