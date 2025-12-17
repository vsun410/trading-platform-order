"""Unit tests for Dashboard V2 app initialization."""

import pytest
from fastapi.testclient import TestClient


class TestDashboardApp:
    """Tests for Dashboard app initialization."""

    def test_app_exists(self):
        """Test that the FastAPI app can be imported."""
        from src.dashboard_v2.main import app

        assert app is not None

    def test_app_title(self):
        """Test that the app has the correct title."""
        from src.dashboard_v2.main import app

        assert app.title == "KimpTrade Dashboard V2"

    def test_root_endpoint_returns_html(self):
        """Test that GET / returns HTML content."""
        from src.dashboard_v2.main import app

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_health_endpoint_exists(self):
        """Test that /api/health endpoint exists."""
        from src.dashboard_v2.main import app

        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
