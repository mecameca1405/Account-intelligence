"""
test_api.py — Basic API tests using FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """API health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """Root endpoint should return service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "AI for Account Intelligence"


def test_login_invalid_credentials():
    """Login with wrong credentials should return 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "noeexiste@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_protected_route_without_token():
    """Accessing protected endpoint without token should return 401."""
    response = client.get("/api/v1/accounts")
    assert response.status_code == 401
