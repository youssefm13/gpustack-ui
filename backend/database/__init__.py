"""
Database package for GPUStack UI.
Provides SQLAlchemy models and database utilities.
"""

from database.connection import get_database, close_database, create_tables
from database.models import User, UserSession, UserPreference

__all__ = [
    "get_database",
    "close_database", 
    "create_tables",
    "User",
    "UserSession",
    "UserPreference"
]
