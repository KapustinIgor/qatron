"""API tests for orchestrator using FastAPI TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_healthy() -> None:
    """Health check endpoint returns 200 and status healthy."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readyz_returns_ready() -> None:
    """Readiness endpoint returns 200 and status ready."""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
