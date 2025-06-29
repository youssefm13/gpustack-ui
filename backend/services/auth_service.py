"""
Authentication service that integrates with GPUStack user management.
"""

import os
import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config.settings import settings

from models.user import (
    User, UserLogin, UserResponse, TokenData, TokenResponse, 
    AuthError, PermissionError
)


class AuthService:
    """Authentication service with GPUStack integration."""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
        
        # GPUStack configuration
        self.gpustack_base_url = settings.gpustack_api_base
        self.gpustack_api_key = settings.gpustack_api_token
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # In-memory session storage (replace with database in production)
        self.active_sessions: Dict[str, Dict] = {}
        self.blacklisted_tokens: set = set()
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token for user."""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        jti = str(uuid.uuid4())
        
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "jti": jti,
            "type": "access"
        }
        
        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        
        # Store session info
        self.active_sessions[jti] = {
            "user_id": user.id,
            "username": user.username,
            "expires_at": expire,
            "token_type": "access"
        }
        
        return token
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token for user."""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        jti = str(uuid.uuid4())
        
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "jti": jti,
            "type": "refresh"
        }
        
        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        
        # Store session info
        self.active_sessions[jti] = {
            "user_id": user.id,
            "username": user.username,
            "expires_at": expire,
            "token_type": "refresh"
        }
        
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            
            # Check if token is blacklisted
            if jti in self.blacklisted_tokens:
                raise AuthError("Token has been revoked", 401)
            
            # For development: Skip session validation if sessions are lost
            # In production, use persistent storage for sessions
            if jti in self.active_sessions:
                session = self.active_sessions[jti]
                if datetime.utcnow() > session["expires_at"]:
                    # Clean up expired session
                    del self.active_sessions[jti]
                    raise AuthError("Token has expired", 401)
            else:
                # Session not found (likely due to restart), but token is still valid
                # Check token expiration directly from payload
                if datetime.utcnow().timestamp() > payload.get("exp", 0):
                    raise AuthError("Token has expired", 401)
            
            return TokenData(**payload)
            
        except JWTError:
            raise AuthError("Invalid token", 401)
    
    async def get_gpustack_users(self) -> list[User]:
        """Fetch users from GPUStack API."""
        if not self.gpustack_api_key:
            raise AuthError("GPUStack API key not configured", 500)
        
        headers = {"Authorization": f"Bearer {self.gpustack_api_key}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.gpustack_base_url}/v1/users",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    users = []
                    for user_data in data.get("items", []):
                        user = User(**user_data)
                        users.append(user)
                    return users
                else:
                    raise AuthError(f"Failed to fetch users from GPUStack: {response.status_code}", 500)
                    
        except httpx.RequestError as e:
            raise AuthError(f"Error connecting to GPUStack: {str(e)}", 500)
    
    async def validate_user_credentials(self, username: str, password: str) -> Optional[User]:
        """Validate user credentials against GPUStack."""
        try:
            users = await self.get_gpustack_users()

            # Find user by username
            user = None
            for u in users:
                if u.username == username:
                    user = u
                    break

            if not user:
                return None

            # Placeholder for password validation
            # Assumes a valid password is provided
            # Future integration required here

            return user

        except AuthError:
            raise
        except Exception as e:
            # If GPUStack is not available, only allow known test credentials
            if username == "admin" and password == "admin":
                return User(
                    id=99999,  # Use a numeric ID
                    username="admin",
                    full_name="Admin User",
                    is_admin=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            raise AuthError("Authentication service unavailable.", 503)
    
    async def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.validate_user_credentials(login_data.username, login_data.password)
        
        if not user:
            raise AuthError("Invalid username or password", 401)
        
        # Create tokens
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,
            user=user_response
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            token_data = self.verify_token(refresh_token)
            
            # Verify it's a refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                raise AuthError("Invalid token type", 401)
            
            # Get user data
            users = await self.get_gpustack_users()
            user = None
            for u in users:
                if u.id == token_data.user_id:
                    user = u
                    break
            
            if not user:
                raise AuthError("User not found", 401)
            
            # Create new access token
            access_token = self.create_access_token(user)
            
            user_response = UserResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Keep the same refresh token
                expires_in=self.access_token_expire_minutes * 60,
                user=user_response
            )
            
        except AuthError:
            raise
        except Exception as e:
            raise AuthError(f"Token refresh failed: {str(e)}", 401)
    
    def logout_user(self, token: str) -> bool:
        """Logout user by blacklisting token."""
        try:
            token_data = self.verify_token(token)
            jti = token_data.jti
            
            # Add to blacklist
            self.blacklisted_tokens.add(jti)
            
            # Remove from active sessions
            if jti in self.active_sessions:
                del self.active_sessions[jti]
            
            return True
            
        except AuthError:
            return False
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from token."""
        token_data = self.verify_token(token)
        
        # Handle test user (ID 99999)
        if token_data.user_id == 99999:
            return User(
                id=99999,
                username="admin", 
                full_name="Admin User",
                is_admin=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        # Get user data from GPUStack
        try:
            users = await self.get_gpustack_users()
            for user in users:
                if user.id == token_data.user_id:
                    return user
        except AuthError:
            # If GPUStack is not available, but we have a valid token
            # Create a basic user from token data
            return User(
                id=token_data.user_id,
                username=token_data.username,
                full_name=token_data.username,
                is_admin=token_data.is_admin,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        raise AuthError("User not found", 404)
    
    def require_admin(self, user: User) -> None:
        """Check if user has admin permissions."""
        if not user.is_admin:
            raise PermissionError("Admin access required")
    
    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions and tokens."""
        now = datetime.utcnow()
        expired_jtis = []
        
        for jti, session in self.active_sessions.items():
            if now > session["expires_at"]:
                expired_jtis.append(jti)
        
        for jti in expired_jtis:
            del self.active_sessions[jti]
            self.blacklisted_tokens.discard(jti)


# Global auth service instance
auth_service = AuthService()
