"""
Authentication middleware for request protection and user context.
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated

from services.auth_service import auth_service
from models.user import User, AuthError, PermissionError


# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[User]:
    """Get current user from token, return None if no token or invalid."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except AuthError:
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """Get current user from token, raise exception if not authenticated."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current user and ensure they have admin privileges."""
    try:
        auth_service.require_admin(current_user)
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


class JWTMiddleware:
    """
    JWT Authentication Middleware for FastAPI.
    
    This middleware extracts and validates JWT tokens from requests,
    setting user context when available. It does not block requests
    for endpoints that don't require authentication.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Process HTTP requests through JWT middleware."""
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
                # Validate token and get user (optional)
                user = await auth_service.get_current_user(token)
                # Store user in scope for downstream use
                scope["user"] = user
            except Exception:
                # Token invalid, but don't block request
                # Individual endpoints will handle auth requirements
                scope["user"] = None
        else:
            scope["user"] = None
        
        await self.app(scope, receive, send)
