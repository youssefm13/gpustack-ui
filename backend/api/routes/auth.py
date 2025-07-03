"""
Authentication API routes for login, logout, refresh, and user management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List, Annotated

from services.auth_service_enhanced import enhanced_auth_service
from middleware.auth_enhanced import get_current_user, get_current_admin_user, security
from models.user import (
    UserLogin, TokenResponse, UserResponse, 
    AuthError
)
from database.models import User


router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """
    Authenticate user with username and password.
    
    Returns JWT access and refresh tokens on successful authentication.
    """
    try:
        token_response = await enhanced_auth_service.authenticate_user(login_data)
        return token_response
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout")
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Logout current user by invalidating their token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    token = credentials.credentials
    success = await enhanced_auth_service.logout_user(token)
    
    if success:
        return {"message": "Successfully logged out"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Refresh access token using refresh token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        token_response = await enhanced_auth_service.refresh_access_token(credentials.credentials)
        return token_response
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    """
    List all users (admin only).
    """
    try:
        users = await enhanced_auth_service.get_gpustack_users()
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/sessions")
async def get_active_sessions(
    admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Get active user sessions (admin only).
    """
    # Get active sessions from enhanced service
    sessions = await enhanced_auth_service.get_active_sessions()
    return {
        "active_sessions": sessions,
        "total_count": len(sessions)
    }


@router.post("/cleanup")
async def cleanup_expired_sessions(
    admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Manually cleanup expired sessions and tokens (admin only).
    """
    cleaned_count = await enhanced_auth_service.cleanup_expired_sessions()
    
    return {
        "message": "Expired sessions cleaned up",
        "cleaned_sessions": cleaned_count
    }
