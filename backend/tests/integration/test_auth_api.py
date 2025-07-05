"""
Integration tests for authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestAuthAPI:
    """Test cases for authentication API endpoints."""

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint is accessible without authentication."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @patch('services.auth_service.AuthService.get_gpustack_users')
    @patch('services.auth_service.AuthService.validate_user_credentials')
    def test_login_success(self, mock_validate, mock_get_users, client: TestClient):
        """Test successful login."""
        from models.user import User
        from datetime import datetime, timezone
        
        # Mock user validation and GPUStack users
        test_user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            email="test@example.com",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_validate.return_value = test_user
        mock_get_users.return_value = [test_user]
        
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422  # Validation error

    @patch('services.auth_service.AuthService.validate_user_credentials')
    def test_login_invalid_credentials(self, mock_validate, client: TestClient):
        """Test login with invalid credentials."""
        mock_validate.return_value = None
        
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_me_endpoint_without_auth(self, client: TestClient):
        """Test /me endpoint without authentication."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401

    def test_me_endpoint_with_invalid_token(self, client: TestClient):
        """Test /me endpoint with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401

    def test_me_endpoint_with_valid_token(self, client: TestClient, auth_headers):
        """Test /me endpoint with valid token."""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert data["username"] == "testuser"

    def test_logout_without_auth(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 401

    def test_logout_with_valid_token(self, client: TestClient, auth_headers):
        """Test logout with valid token."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    def test_refresh_token_without_auth(self, client: TestClient):
        """Test token refresh without authentication."""
        response = client.post("/api/auth/refresh")
        
        assert response.status_code == 401

    def test_refresh_token_with_access_token(self, client: TestClient, auth_headers):
        """Test token refresh with access token (should fail)."""
        response = client.post("/api/auth/refresh", headers=auth_headers)
        
        # Should fail because we need a refresh token, not access token
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""

    def test_models_endpoint_without_auth(self, client: TestClient):
        """Test models endpoint (no auth required but may fail if GPUStack unavailable)."""
        response = client.get("/api/models")
        
        # Models endpoint doesn't require auth but may return 500 if GPUStack is unavailable
        assert response.status_code in [200, 500]

    def test_inference_endpoint_without_auth(self, client: TestClient):
        """Test inference endpoint requires authentication."""
        response = client.post(
            "/api/inference/infer",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}]
            }
        )
        
        assert response.status_code == 401

    def test_tools_search_without_auth(self, client: TestClient):
        """Test search endpoint requires authentication."""
        response = client.post(
            "/api/tools/search",
            json={"q": "test query"}
        )
        
        assert response.status_code == 401

    def test_file_upload_without_auth(self, client: TestClient):
        """Test file upload requires authentication."""
        response = client.post(
            "/api/files/upload",
            files={"file": ("test.txt", "test content", "text/plain")}
        )
        
        assert response.status_code == 401
