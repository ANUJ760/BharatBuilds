"""Basic health endpoint test."""
from fastapi.testclient import TestClient


class TestHealth:
    """Health endpoint tests."""

    def test_health(self):
        from backend.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
