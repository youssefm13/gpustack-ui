"""
SQLAlchemy database models for GPUStack UI.
"""

import json
from datetime import datetime
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, UniqueConstraint, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from database.connection import Base

class User(Base):
    """User model with enhanced authentication features."""
    
    __tablename__ = "users"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    
    # Status and permissions
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # GPUStack integration
    gpustack_user_id = Column(Integer, nullable=True, unique=True)
    
    # Preferences as JSON
    preferences_json = Column(Text, nullable=True, name="preferences")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_username_active', 'username', 'is_active'),
        Index('idx_email_active', 'email', 'is_active'),
    )
    
    @hybrid_property
    def preferences_dict(self) -> Dict[str, Any]:
        """Get preferences as a dictionary."""
        if self.preferences_json:
            try:
                return json.loads(self.preferences_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @preferences_dict.setter
    def preferences_dict(self, value: Dict[str, Any]) -> None:
        """Set preferences from a dictionary."""
        self.preferences_json = json.dumps(value) if value else None
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value."""
        prefs = self.preferences_dict
        return prefs.get(key, default)
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a specific preference value."""
        prefs = self.preferences_dict
        prefs[key] = value
        self.preferences_dict = prefs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "gpustack_user_id": self.gpustack_user_id,
            "preferences": self.preferences_dict,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', is_admin={self.is_admin})>"


class UserSession(Base):
    """User session model for persistent authentication."""
    
    __tablename__ = "user_sessions"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token information
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    
    # Expiration
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Timestamps and metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_token_type', 'user_id', 'token_type'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_user_expires', 'user_id', 'expires_at'),
    )
    
    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_last_accessed(self) -> None:
        """Update the last accessed timestamp."""
        self.last_accessed = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "jti": self.jti,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_expired": self.is_expired()
        }
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, type='{self.token_type}')>"


class UserPreference(Base):
    """Individual user preferences for fine-grained control."""
    
    __tablename__ = "user_preferences"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Preference data
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'preference_key', name='uq_user_preference'),
        Index('idx_user_preference_key', 'user_id', 'preference_key'),
    )
    
    @property
    def value(self) -> Any:
        """Get the preference value, attempting to parse as JSON."""
        if self.preference_value is None:
            return None
        
        # Try to parse as JSON
        try:
            return json.loads(self.preference_value)
        except (json.JSONDecodeError, TypeError):
            # Return as string if not valid JSON
            return self.preference_value
    
    @value.setter
    def value(self, val: Any) -> None:
        """Set the preference value, converting to JSON if needed."""
        if val is None:
            self.preference_value = None
        elif isinstance(val, (str, int, float, bool)):
            self.preference_value = str(val)
        else:
            # Convert complex types to JSON
            self.preference_value = json.dumps(val)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preference to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "key": self.preference_key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, key='{self.preference_key}')>"


class Conversation(Base):
    """Model for storing conversation history."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=True)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")


class Message(Base):
    """Model for storing messages within a conversation."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


# Common preference keys (constants)
class PreferenceKeys:
    """Constants for common preference keys."""
    
    # UI preferences
    THEME = "theme"  # "light" or "dark"
    LANGUAGE = "language"  # "en", "es", etc.
    
    # Model preferences
    DEFAULT_MODEL = "default_model"
    DEFAULT_TEMPERATURE = "default_temperature"
    DEFAULT_MAX_TOKENS = "default_max_tokens"
    
    # Chat preferences
    ENABLE_STREAMING = "enable_streaming"
    SHOW_METRICS = "show_metrics"
    AUTO_SAVE_CONVERSATIONS = "auto_save_conversations"
    
    # File processing preferences
    DEFAULT_FILE_PROCESSING = "default_file_processing"
    MAX_FILE_SIZE_MB = "max_file_size_mb"
    
    # Search preferences
    ENABLE_WEB_SEARCH = "enable_web_search"
    DEFAULT_SEARCH_ENGINE = "default_search_engine"
