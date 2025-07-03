"""
Enhanced authentication middleware with database integration.
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated

from services.auth_service_enhanced import enhanced_auth_service
from database.models import User as DBUser
from models.user import AuthError, PermissionError

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


async def get_current_user_optional_enhanced(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[DBUser]:
    """Get current user from token using enhanced auth service, return None if no token or invalid."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await enhanced_auth_service.get_current_user(token)
        return user
    except AuthError:
        return None


async def get_current_user_enhanced(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> DBUser:
    """Get current user from token using enhanced auth service, raise exception if not authenticated."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user = await enhanced_auth_service.get_current_user(token)
        return user
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user_enhanced(
    current_user: Annotated[DBUser, Depends(get_current_user_enhanced)]
) -> DBUser:
    """Get current user and ensure they have admin privileges using enhanced auth service."""
    try:
        enhanced_auth_service.require_admin(current_user)
        return current_user
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


def extract_token_from_request(request: Request) -> Optional[str]:
    """Extract token from request headers."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None


class EnhancedJWTMiddleware:
    """
    Enhanced JWT Authentication Middleware with database integration.
    
    This middleware extracts and validates JWT tokens from requests using
    the enhanced authentication service with database session validation.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Process HTTP requests through enhanced JWT middleware."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create request object to extract token
        from fastapi import Request
        request = Request(scope, receive)
        
        # Extract token from request
        token = extract_token_from_request(request)
        
        if token:
            try:
                # Validate token and get user using enhanced auth service
                user = await enhanced_auth_service.get_current_user(token)
                # Store user in scope for downstream use
                scope["user"] = user
                scope["auth_type"] = "enhanced"
            except Exception:
                # Token invalid, but don't block request
                # Individual endpoints will handle auth requirements
                scope["user"] = None
                scope["auth_type"] = None
        else:
            scope["user"] = None
            scope["auth_type"] = None
        
        await self.app(scope, receive, send)


# Dependency injection helpers for enhanced database operations
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_database


async def get_current_user_with_db(
    current_user: Annotated[DBUser, Depends(get_current_user_enhanced)],
    db: AsyncSession = Depends(get_database)
) -> tuple[DBUser, AsyncSession]:
    """Get current user and database session together."""
    return current_user, db


async def get_current_admin_with_db(
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)],
    db: AsyncSession = Depends(get_database)
) -> tuple[DBUser, AsyncSession]:
    """Get current admin user and database session together."""
    return admin_user, db


# Aliases for backwards compatibility
get_current_user = get_current_user_enhanced
get_current_admin_user = get_current_admin_user_enhanced
get_current_user_optional = get_current_user_optional_enhanced
