"""Base API client for test automation."""
import os
from typing import Dict, Optional

import requests


class APIClient:
    """Base API client with authentication and error handling."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client.

        Args:
            base_url: Base URL of the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("API_KEY")

    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return requests.get(url, headers=self._headers(), **kwargs)

    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return requests.post(url, json=json, headers=self._headers(), **kwargs)

    def put(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PUT request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return requests.put(url, json=json, headers=self._headers(), **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return requests.delete(url, headers=self._headers(), **kwargs)
