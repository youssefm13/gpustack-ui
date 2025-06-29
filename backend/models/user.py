"""
User models and data structures for authentication system.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    """User model matching GPUStack user structure."""
    model_config = ConfigDict(extra="allow")
    
    id: int
    username: str
    full_name: str
    is_admin: bool = False
    require_password_change: bool = False
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Model for creating new users."""
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    is_admin: bool = False


class UserLogin(BaseModel):
    """Model for user login credentials."""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Model for user data in API responses."""
    id: int
    username: str
    full_name: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class TokenData(BaseModel):
    """Model for JWT token payload."""
    user_id: int
    username: str
    is_admin: bool
    exp: int
    iat: int
    jti: str  # JWT ID for token blacklisting


class TokenResponse(BaseModel):
    """Model for login response with tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Model for token refresh requests."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Model for password change requests."""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UserSession(BaseModel):
    """Model for user session tracking."""
    id: Optional[int] = None
    user_id: int
    token_jti: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PermissionError(Exception):
    """Custom exception for permission errors."""
    def __init__(self, message: str = "Insufficient permissions"):
        self.message = message
        super().__init__(self.message)
