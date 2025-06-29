"""
Unit tests for authentication service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jose import jwt

from services.auth_service import AuthService
from models.user import User


class TestAuthService:
    """Test cases for AuthService."""

    def test_create_access_token(self):
        """Test access token creation."""
        auth_service = AuthService()
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        token = auth_service.create_access_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
        assert decoded["username"] == "testuser"
        assert decoded["user_id"] == 1
        assert decoded["is_admin"] is False

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        auth_service = AuthService()
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        token = auth_service.create_refresh_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
        assert decoded["sub"] == "testuser"
        assert decoded["type"] == "refresh"

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        auth_service = AuthService()
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        token = auth_service.create_access_token(user)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["username"] == "testuser"
        assert payload["user_id"] == 1

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        auth_service = AuthService()
        
        payload = auth_service.verify_token("invalid-token")
        
        assert payload is None

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        auth_service = AuthService()
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create token with negative expiry (already expired)
        with patch.object(auth_service, 'access_token_expire_minutes', -1):
            token = auth_service.create_access_token(user)
            
        payload = auth_service.verify_token(token)
        
        assert payload is None

    @patch('services.auth_service.httpx.AsyncClient.get')
    async def test_get_gpustack_users_success(self, mock_get):
        """Test successful GPUStack users retrieval."""
        auth_service = AuthService()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 1,
                    "name": "testuser",
                    "display_name": "Test User",
                    "email": "test@example.com"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        users = await auth_service.get_gpustack_users()
        
        assert len(users) == 1
        assert users[0]["name"] == "testuser"
        assert users[0]["display_name"] == "Test User"

    @patch('services.auth_service.httpx.AsyncClient.get')
    async def test_get_gpustack_users_failure(self, mock_get):
        """Test GPUStack users retrieval failure."""
        auth_service = AuthService()
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        users = await auth_service.get_gpustack_users()
        
        assert users == []

    def test_validate_user_credentials_valid(self):
        """Test user credential validation with valid credentials."""
        auth_service = AuthService()
        
        # For now, all credentials are valid (placeholder implementation)
        is_valid = auth_service.validate_user_credentials("testuser", "password")
        
        assert is_valid is True

    def test_is_session_blacklisted_false(self):
        """Test session blacklist check for non-blacklisted session."""
        auth_service = AuthService()
        
        is_blacklisted = auth_service.is_session_blacklisted("session-123")
        
        assert is_blacklisted is False

    def test_blacklist_session(self):
        """Test session blacklisting."""
        auth_service = AuthService()
        session_id = "session-123"
        
        auth_service.blacklist_session(session_id)
        
        assert auth_service.is_session_blacklisted(session_id) is True

    def test_create_session(self):
        """Test session creation."""
        auth_service = AuthService()
        user_data = {
            "id": 1,
            "username": "testuser"
        }
        
        session = auth_service.create_session(user_data)
        
        assert session.user_id == 1
        assert session.username == "testuser"
        assert session.session_id is not None
        assert session.is_active is True
        assert session.created_at is not None

    def test_get_session_valid(self):
        """Test retrieving valid session."""
        auth_service = AuthService()
        user_data = {
            "id": 1,
            "username": "testuser"
        }
        
        session = auth_service.create_session(user_data)
        retrieved_session = auth_service.get_session(session.session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session.session_id
        assert retrieved_session.user_id == 1

    def test_get_session_invalid(self):
        """Test retrieving invalid session."""
        auth_service = AuthService()
        
        session = auth_service.get_session("invalid-session-id")
        
        assert session is None
