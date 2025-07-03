"""
Unit tests for authentication service.
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service_enhanced import enhanced_auth_service, EnhancedAuthService
from database.models import User as DBUser
from models.user import User, AuthError
from database.connection import get_db_session


class TestAuthService:
    """Test cases for AuthService."""

    def test_create_access_token(self):
        """Test access token creation."""
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        token = enhanced_auth_service.create_access_token_sync(user)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(token, enhanced_auth_service.secret_key, algorithms=[enhanced_auth_service.algorithm])
        assert decoded["username"] == "testuser"
        assert decoded["user_id"] == 1
        assert decoded["is_admin"] is False

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        # Using enhanced_auth_service singleton
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        token = enhanced_auth_service.create_refresh_token_sync(user)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(token, enhanced_auth_service.secret_key, algorithms=[enhanced_auth_service.algorithm])
        assert decoded["username"] == "testuser"
        assert decoded["type"] == "refresh"

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        # Using enhanced_auth_service singleton
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        token = enhanced_auth_service.create_access_token_sync(user)
        payload = enhanced_auth_service.verify_token_sync(token)
        
        assert payload is not None
        assert payload.username == "testuser"
        assert payload.user_id == 1

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        # Using enhanced_auth_service singleton
        
        with pytest.raises(AuthError) as excinfo:
            enhanced_auth_service.verify_token_sync("invalid-token")
        
        assert str(excinfo.value) == "Invalid token"

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        # Using enhanced_auth_service singleton
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Create token with negative expiry (already expired)
        with patch.object(enhanced_auth_service, 'access_token_expire_minutes', -1):
            token = enhanced_auth_service.create_access_token_sync(user)
            
        with pytest.raises(AuthError):
            enhanced_auth_service.verify_token_sync(token)

    @patch('services.enhanced_auth_service.httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_get_gpustack_users_success(self, mock_get):
        """Test successful GPUStack users retrieval."""
        import os
        # Ensure the API token is in the environment variables
        os.environ["GPUSTACK_API_TOKEN"] = "test-gpustack-token"
        os.environ["GPUSTACK_API_BASE"] = "http://localhost:8080"
        
        # Using enhanced_auth_service singleton
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 1,
                    "username": "testuser",
                    "full_name": "Test User",
                    "email": "test@example.com",
                    "is_admin": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        mock_get.return_value = mock_response
        
        users = await enhanced_auth_service.get_gpustack_users()
        
        assert len(users) == 1
        assert users[0].username == "testuser"
        assert users[0].full_name == "Test User"

    @patch('services.enhanced_auth_service.httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_get_gpustack_users_failure(self, mock_get):
        """Test GPUStack users retrieval failure."""
        # Using enhanced_auth_service singleton
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(AuthError):
            await enhanced_auth_service.get_gpustack_users()

    @pytest.mark.asyncio
    async def test_validate_user_credentials_valid(self):
        """Test user credential validation with valid credentials."""
        # Using enhanced_auth_service singleton
        
        with patch.object(enhanced_auth_service, 'get_gpustack_users') as mock_get_users:
            mock_user = User(
                id=1,
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            mock_get_users.return_value = [mock_user]
            
            user = await enhanced_auth_service.validate_user_credentials("testuser", "password")
            
            assert user is not None
            assert user.username == "testuser"

    def test_logout_user(self):
        """Test user logout functionality."""
        # Using enhanced_auth_service singleton
        user = User(
            id=1,
            username="testuser",
            full_name="Test User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Create token and logout
        token = enhanced_auth_service.create_access_token_sync(user)
        result = enhanced_auth_service.logout_user_sync(token)
        
        assert result is True
        
        # Token should now be blacklisted
        with pytest.raises(AuthError):
            enhanced_auth_service.verify_token_sync(token)


class TestEnhancedAuthService:
    """Test cases for EnhancedAuthService with database integration."""
    
    @pytest.mark.asyncio
    async def test_create_access_token_with_db(self):
        """Test access token creation with database session."""
        # Create a test user in database
        db = await get_db_session()
        try:
            # Create test user
            test_user = DBUser(
                username="testuser_db",
                email="test@example.com",
                password_hash=enhanced_auth_service.hash_password("testpass"),
                full_name="Test User DB",
                is_admin=False,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            
            # Create access token
            token = await enhanced_auth_service.create_access_token(test_user, db)
            
            assert token is not None
            assert isinstance(token, str)
            
            # Verify token can be decoded
            decoded = jwt.decode(token, enhanced_auth_service.secret_key, algorithms=[enhanced_auth_service.algorithm])
            assert decoded["username"] == "testuser_db"
            assert decoded["user_id"] == test_user.id
            
        finally:
            # Clean up
            if test_user.id:
                await db.delete(test_user)
                await db.commit()
            await db.close()
    
    @pytest.mark.asyncio 
    async def test_verify_token_with_db(self):
        """Test token verification with database session validation."""
        db = await get_db_session()
        try:
            # Create test user
            test_user = DBUser(
                username="testuser_verify",
                email="verify@example.com",
                password_hash=enhanced_auth_service.hash_password("testpass"),
                full_name="Test Verify User",
                is_admin=False,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            
            # Create token
            token = await enhanced_auth_service.create_access_token(test_user, db)
            
            # Verify token
            token_data = await enhanced_auth_service.verify_token(token, db)
            
            assert token_data is not None
            assert token_data.username == "testuser_verify"
            assert token_data.user_id == test_user.id
            
        finally:
            # Clean up
            if test_user.id:
                await db.delete(test_user)
                await db.commit()
            await db.close()
    
    @pytest.mark.asyncio
    async def test_logout_user_with_db(self):
        """Test user logout with database session removal."""
        db = await get_db_session()
        try:
            # Create test user
            test_user = DBUser(
                username="testuser_logout",
                email="logout@example.com",
                password_hash=enhanced_auth_service.hash_password("testpass"),
                full_name="Test Logout User", 
                is_admin=False,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            
            # Create token
            token = await enhanced_auth_service.create_access_token(test_user, db)
            
            # Verify token works
            token_data = await enhanced_auth_service.verify_token(token, db)
            assert token_data is not None
            
            # Logout user
            result = await enhanced_auth_service.logout_user(token)
            assert result is True
            
            # Token should now be invalid (session removed from DB)
            with pytest.raises(AuthError):
                await enhanced_auth_service.verify_token(token, db)
            
        finally:
            # Clean up
            if test_user.id:
                await db.delete(test_user)
                await db.commit()
            await db.close()
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_db(self):
        """Test getting current user from token with database lookup."""
        db = await get_db_session()
        try:
            # Create test user
            test_user = DBUser(
                username="testuser_current",
                email="current@example.com",
                password_hash=enhanced_auth_service.hash_password("testpass"),
                full_name="Test Current User",
                is_admin=False,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            
            # Create token
            token = await enhanced_auth_service.create_access_token(test_user, db)
            
            # Get current user from token
            current_user = await enhanced_auth_service.get_current_user(token)
            
            assert current_user is not None
            assert current_user.username == "testuser_current"
            assert current_user.id == test_user.id
            
        finally:
            # Clean up
            if test_user.id:
                await db.delete(test_user)
                await db.commit()
            await db.close()
