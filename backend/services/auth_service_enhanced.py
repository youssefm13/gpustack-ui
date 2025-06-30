"""
Enhanced authentication service with database persistence for GPUStack UI.
"""

import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Request
from config.settings import settings
from database.connection import get_db_session
from database.models import User, UserSession, UserPreference, PreferenceKeys
# Define classes locally since they were previously in models.user
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = False
    exp: Optional[int] = None
    jti: Optional[str] = None
    type: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class PermissionError(Exception):
    def __init__(self, message: str, status_code: int = 403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class EnhancedAuthService:
    """Enhanced authentication service with database persistence."""
    
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
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def create_access_token(self, user: User, db: AsyncSession, 
                                request: Optional[Request] = None) -> str:
        """Create JWT access token and store session in database."""
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
        
        # Store session in database
        session = UserSession(
            user_id=user.id,
            session_token=token,
            jti=jti,
            token_type="access",
            expires_at=expire,
            ip_address=getattr(request.client, 'host', None) if request and hasattr(request, 'client') else None,
            user_agent=request.headers.get('user-agent') if request else None
        )
        
        db.add(session)
        await db.commit()
        
        return token
    
    async def create_refresh_token(self, user: User, db: AsyncSession,
                                 request: Optional[Request] = None) -> str:
        """Create JWT refresh token and store session in database."""
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
        
        # Store session in database
        session = UserSession(
            user_id=user.id,
            session_token=token,
            jti=jti,
            token_type="refresh",
            expires_at=expire,
            ip_address=getattr(request.client, 'host', None) if request and hasattr(request, 'client') else None,
            user_agent=request.headers.get('user-agent') if request else None
        )
        
        db.add(session)
        await db.commit()
        
        return token
    
    async def verify_token(self, token: str, db: AsyncSession) -> TokenData:
        """Verify and decode JWT token with database session validation."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            
            if not jti:
                raise AuthError("Invalid token format", 401)
            
            # Check session in database
            session_query = select(UserSession).where(
                UserSession.jti == jti,
                UserSession.session_token == token
            )
            result = await db.execute(session_query)
            session = result.scalar_one_or_none()
            
            if not session:
                raise AuthError("Session not found", 401)
            
            if session.is_expired():
                # Clean up expired session
                await db.delete(session)
                await db.commit()
                raise AuthError("Token has expired", 401)
            
            # Update last accessed time
            session.update_last_accessed()
            await db.commit()
            
            return TokenData(**payload)
            
        except JWTError:
            raise AuthError("Invalid token", 401)
    
    async def get_user_by_username(self, username: str, db: AsyncSession) -> Optional[User]:
        """Get user by username from database."""
        query = select(User).where(
            User.username == username,
            User.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        """Get user by ID from database."""
        query = select(User).where(
            User.id == user_id,
            User.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_user(self, username: str, password: str, email: str = None,
                         full_name: str = None, is_admin: bool = False,
                         db: AsyncSession = None) -> User:
        """Create a new user in the database."""
        if db is None:
            db = await get_db_session()
        
        # Check if user already exists
        existing_user = await self.get_user_by_username(username, db)
        if existing_user:
            raise AuthError(f"User '{username}' already exists", 400)
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            full_name=full_name,
            is_admin=is_admin,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def validate_local_credentials(self, username: str, password: str,
                                       db: AsyncSession) -> Optional[User]:
        """Validate user credentials against local database."""
        user = await self.get_user_by_username(username, db)
        
        if not user or not user.password_hash:
            return None
        
        if self.verify_password(password, user.password_hash):
            # Update last login
            user.update_last_login()
            await db.commit()
            return user
        
        return None
    
    async def validate_gpustack_credentials(self, username: str, password: str) -> Optional[Dict]:
        """Validate credentials against GPUStack (placeholder for future implementation)."""
        # This is a placeholder for actual GPUStack authentication
        # For now, we'll simulate GPUStack API calls
        
        if not self.gpustack_api_key:
            return None
        
        headers = {"Authorization": f"Bearer {self.gpustack_api_key}"}
        
        try:
            async with httpx.AsyncClient() as client:
                # This would be the actual GPUStack authentication endpoint
                response = await client.get(
                    f"{self.gpustack_base_url}/v1/users",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Look for user in GPUStack users
                    for user_data in data.get("items", []):
                        if user_data.get("username") == username:
                            # In a real implementation, you would validate the password here
                            return user_data
                
        except httpx.RequestError:
            # GPUStack is not available
            return None
        
        return None
    
    async def sync_gpustack_user(self, gpustack_user: Dict, db: AsyncSession) -> User:
        """Sync a GPUStack user with local database."""
        username = gpustack_user.get("username")
        email = gpustack_user.get("email")
        full_name = gpustack_user.get("full_name", username)
        gpustack_id = gpustack_user.get("id")
        
        # Check if user exists locally
        user = await self.get_user_by_username(username, db)
        
        if user:
            # Update existing user
            user.email = email
            user.full_name = full_name
            user.gpustack_user_id = gpustack_id
            user.updated_at = datetime.utcnow()
        else:
            # Create new user from GPUStack data
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                gpustack_user_id=gpustack_id,
                is_admin=False,  # Default to non-admin
                is_active=True
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def authenticate_user(self, login_data: UserLogin, 
                              request: Optional[Request] = None) -> TokenResponse:
        """Authenticate user with enhanced fallback logic."""
        db = await get_db_session()
        
        try:
            # Try local authentication first
            user = await self.validate_local_credentials(login_data.username, login_data.password, db)
            
            if not user:
                # Try GPUStack authentication as fallback
                gpustack_user = await self.validate_gpustack_credentials(
                    login_data.username, login_data.password
                )
                
                if gpustack_user:
                    # Sync with local database
                    user = await self.sync_gpustack_user(gpustack_user, db)
                else:
                    raise AuthError("Invalid username or password", 401)
            
            # Create tokens
            access_token = await self.create_access_token(user, db, request)
            refresh_token = await self.create_refresh_token(user, db, request)
            
            user_response = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_admin=user.is_admin,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.access_token_expire_minutes * 60,
                user=user_response
            )
            
        finally:
            await db.close()
    
    async def refresh_access_token(self, refresh_token: str,
                                 request: Optional[Request] = None) -> TokenResponse:
        """Refresh access token using refresh token."""
        db = await get_db_session()
        
        try:
            token_data = await self.verify_token(refresh_token, db)
            
            # Verify it's a refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                raise AuthError("Invalid token type", 401)
            
            # Get user
            user = await self.get_user_by_id(token_data.user_id, db)
            if not user:
                raise AuthError("User not found", 401)
            
            # Create new access token
            access_token = await self.create_access_token(user, db, request)
            
            user_response = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_admin=user.is_admin,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Keep the same refresh token
                expires_in=self.access_token_expire_minutes * 60,
                user=user_response
            )
            
        finally:
            await db.close()
    
    async def logout_user(self, token: str) -> bool:
        """Logout user by removing session from database."""
        db = await get_db_session()
        
        try:
            token_data = await self.verify_token(token, db)
            jti = token_data.jti
            
            # Remove session from database
            delete_query = delete(UserSession).where(UserSession.jti == jti)
            await db.execute(delete_query)
            await db.commit()
            
            return True
            
        except AuthError:
            return False
        finally:
            await db.close()
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from token with database lookup."""
        db = await get_db_session()
        
        try:
            token_data = await self.verify_token(token, db)
            user = await self.get_user_by_id(token_data.user_id, db)
            
            if not user:
                raise AuthError("User not found", 404)
            
            return user
            
        finally:
            await db.close()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from database."""
        db = await get_db_session()
        
        try:
            # Delete expired sessions
            delete_query = delete(UserSession).where(
                UserSession.expires_at < datetime.utcnow()
            )
            result = await db.execute(delete_query)
            await db.commit()
            
            return result.rowcount
            
        finally:
            await db.close()
    
    async def get_user_sessions(self, user_id: int) -> List[UserSession]:
        """Get all active sessions for a user."""
        db = await get_db_session()
        
        try:
            query = select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.expires_at > datetime.utcnow()
            ).order_by(UserSession.last_accessed.desc())
            
            result = await db.execute(query)
            return result.scalars().all()
            
        finally:
            await db.close()
    
    async def revoke_user_sessions(self, user_id: int, except_jti: str = None) -> int:
        """Revoke all sessions for a user except optionally one."""
        db = await get_db_session()
        
        try:
            query = delete(UserSession).where(UserSession.user_id == user_id)
            
            if except_jti:
                query = query.where(UserSession.jti != except_jti)
            
            result = await db.execute(query)
            await db.commit()
            
            return result.rowcount
            
        finally:
            await db.close()
    
    def require_admin(self, user: User) -> None:
        """Check if user has admin permissions."""
        if not user.is_admin:
            raise PermissionError("Admin access required")


# Global enhanced auth service instance
enhanced_auth_service = EnhancedAuthService()
