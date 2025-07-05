"""
Enhanced authentication API routes with database integration.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from database.connection import get_database
from services.auth_service_enhanced import enhanced_auth_service
from middleware.auth_enhanced import (
    get_current_user_enhanced, get_current_admin_user_enhanced, 
    security
)
from models.user import (
    UserLogin, TokenResponse, RefreshTokenRequest, UserResponse, 
    AuthError
)
from database.models import User as DBUser, UserSession
from api.schemas import (
    UserCreateRequest, SessionResponse,
    UserPreferenceRequest, UserPreferenceResponse
)

router = APIRouter(tags=["Enhanced Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login_enhanced(login_data: UserLogin, request: Request):
    """
    Authenticate user with enhanced database-backed authentication.
    
    Supports both local database users and GPUStack integration.
    Sessions are persisted in the database for cross-restart persistence.
    """
    try:
        token_response = await enhanced_auth_service.authenticate_user(login_data, request)
        return token_response
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout")
async def logout_enhanced(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Logout current user by removing session from database.
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
async def refresh_token_enhanced(refresh_request: RefreshTokenRequest, request: Request):
    """
    Refresh access token using refresh token with database validation.
    """
    try:
        token_response = await enhanced_auth_service.refresh_access_token(
            refresh_request.refresh_token, request
        )
        return token_response
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info_enhanced(
    current_user: Annotated[DBUser, Depends(get_current_user_enhanced)]
):
    """
    Get current authenticated user information from database.
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
async def list_users_enhanced(
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)],
    db: AsyncSession = Depends(get_database)
):
    """
    List all users from database (admin only).
    """
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(DBUser).where(DBUser.is_active == True).order_by(DBUser.username)
        )
        users = result.scalars().all()
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.post("/users", response_model=UserResponse)
async def create_user_enhanced(
    user_data: UserCreateRequest,
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)],
    db: AsyncSession = Depends(get_database)
):
    """
    Create a new user (admin only).
    """
    try:
        user = await enhanced_auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name,
            is_admin=user_data.is_admin,
            db=db
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/sessions", response_model=List[SessionResponse])
async def get_active_sessions_enhanced(
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)]
):
    """
    Get all active user sessions from database (admin only).
    """
    try:
        # Clean up expired sessions first
        cleaned = await enhanced_auth_service.cleanup_expired_sessions()
        
        # Get all active sessions from database
        from database.connection import get_db_session
        from sqlalchemy import select
        from datetime import datetime
        
        db = await get_db_session()
        try:
            result = await db.execute(
                select(UserSession, DBUser.username)
                .join(DBUser, UserSession.user_id == DBUser.id)
                .where(UserSession.expires_at > datetime.utcnow())
                .order_by(UserSession.last_accessed.desc())
            )
            sessions_data = result.all()
            
            sessions = []
            for session, username in sessions_data:
                sessions.append(SessionResponse(
                    id=session.id,
                    user_id=session.user_id,
                    username=username,
                    jti=session.jti,
                    token_type=session.token_type,
                    expires_at=session.expires_at,
                    created_at=session.created_at,
                    last_accessed=session.last_accessed,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent
                ))
            
            return sessions
            
        finally:
            await db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")


@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
async def get_user_sessions_enhanced(
    user_id: int,
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)]
):
    """
    Get active sessions for a specific user (admin only).
    """
    try:
        sessions = await enhanced_auth_service.get_user_sessions(user_id)
        
        return [
            SessionResponse(
                id=session.id,
                user_id=session.user_id,
                username=session.user.username,
                jti=session.jti,
                token_type=session.token_type,
                expires_at=session.expires_at,
                created_at=session.created_at,
                last_accessed=session.last_accessed,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            )
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user sessions: {str(e)}")


@router.delete("/sessions/{user_id}")
async def revoke_user_sessions_enhanced(
    user_id: int,
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)]
):
    """
    Revoke all sessions for a specific user (admin only).
    """
    try:
        revoked_count = await enhanced_auth_service.revoke_user_sessions(user_id)
        
        return {
            "message": f"Revoked {revoked_count} sessions for user {user_id}",
            "revoked_sessions": revoked_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke sessions: {str(e)}")


@router.post("/cleanup")
async def cleanup_expired_sessions_enhanced(
    admin_user: Annotated[DBUser, Depends(get_current_admin_user_enhanced)]
):
    """
    Manually cleanup expired sessions from database (admin only).
    """
    try:
        cleaned_count = await enhanced_auth_service.cleanup_expired_sessions()
        
        return {
            "message": "Expired sessions cleaned up",
            "cleaned_sessions": cleaned_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")


# User preference endpoints
@router.get("/preferences", response_model=List[UserPreferenceResponse])
async def get_user_preferences(
    current_user: Annotated[DBUser, Depends(get_current_user_enhanced)],
    db: AsyncSession = Depends(get_database)
):
    """
    Get current user's preferences.
    """
    try:
        from sqlalchemy import select
        from database.models import UserPreference
        
        result = await db.execute(
            select(UserPreference)
            .where(UserPreference.user_id == current_user.id)
            .order_by(UserPreference.preference_key)
        )
        preferences = result.scalars().all()
        
        return [
            UserPreferenceResponse(
                key=pref.preference_key,
                value=pref.value,
                updated_at=pref.updated_at
            )
            for pref in preferences
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")


@router.post("/preferences")
async def set_user_preference(
    preference_data: UserPreferenceRequest,
    current_user: Annotated[DBUser, Depends(get_current_user_enhanced)],
    db: AsyncSession = Depends(get_database)
):
    """
    Set or update a user preference.
    """
    try:
        from sqlalchemy import select
        from database.models import UserPreference
        from datetime import datetime
        
        # Check if preference exists
        result = await db.execute(
            select(UserPreference).where(
                UserPreference.user_id == current_user.id,
                UserPreference.preference_key == preference_data.key
            )
        )
        existing_pref = result.scalar_one_or_none()
        
        if existing_pref:
            # Update existing preference
            existing_pref.value = preference_data.value
            existing_pref.updated_at = datetime.utcnow()
        else:
            # Create new preference
            new_pref = UserPreference(
                user_id=current_user.id,
                preference_key=preference_data.key,
                preference_value=preference_data.value
            )
            db.add(new_pref)
        
        await db.commit()
        
        return {"message": f"Preference '{preference_data.key}' updated successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update preference: {str(e)}")


@router.get("/health")
async def auth_health_check():
    """
    Check authentication system health.
    """
    try:
        from database.connection import check_database_health
        
        db_health = await check_database_health()
        expired_cleaned = await enhanced_auth_service.cleanup_expired_sessions()
        
        return {
            "status": "healthy",
            "database": db_health,
            "expired_sessions_cleaned": expired_cleaned,
            "auth_service": "enhanced_auth_service active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "auth_service": "enhanced_auth_service error"
        }
