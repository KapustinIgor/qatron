"""API client for QAtron Control Plane."""
from typing import Any, Dict, Optional

import requests

from qatron_cli.config import config


class APIClient:
    """Client for QAtron Control Plane API."""

    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None):
        """Initialize API client."""
        self.api_url = (api_url or config.get_api_url()).rstrip("/")
        self.token = token or config.get_token()

    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> requests.Response:
        """Make HTTP request."""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method, url, headers=self._headers(), **kwargs
        )
        response.raise_for_status()
        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        return self._request("POST", endpoint, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make PUT request."""
        return self._request("PUT", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)
