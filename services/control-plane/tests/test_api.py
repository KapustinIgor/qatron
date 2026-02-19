"""API tests for control-plane using FastAPI TestClient."""


def test_healthz_returns_healthy(client):
    """Health check endpoint returns 200 and status healthy."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readyz_returns_ready(client):
    """Readiness endpoint returns 200 and status ready."""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_metrics_endpoint_exists(client):
    """Prometheus /metrics endpoint returns 200."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_protected_projects_requires_auth(client):
    """GET /api/v1/projects without auth returns 403 (HTTPBearer)."""
    response = client.get("/api/v1/projects")
    # FastAPI HTTPBearer returns 403 when no Authorization header
    assert response.status_code == 403


def test_docs_available(client):
    """OpenAPI docs are served at /docs."""
    response = client.get("/docs")
    assert response.status_code == 200
