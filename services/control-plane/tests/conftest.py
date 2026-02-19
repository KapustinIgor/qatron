"""Pytest fixtures for control-plane tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client (lifespan runs on enter)."""
    return TestClient(app)
