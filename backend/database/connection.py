"""
Database connection and session management for GPUStack UI.
"""

import os
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

# Create the base class for all database models
Base = declarative_base()

# Database engines
_async_engine = None
_async_session_factory = None

def get_database_url() -> str:
    """Get the database URL for async operations."""
    db_url = settings.database_url
    
    # Convert SQLite URL to async version
    if db_url.startswith("sqlite:///"):
        # For SQLite, use aiosqlite
        return db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif db_url.startswith("postgresql://"):
        # For PostgreSQL, use asyncpg
        return db_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        return db_url

def get_sync_database_url() -> str:
    """Get the database URL for synchronous operations (migrations)."""
    return settings.database_url

async def get_async_engine():
    """Get or create the async database engine."""
    global _async_engine
    
    if _async_engine is None:
        database_url = get_database_url()
        _async_engine = create_async_engine(
            database_url,
            echo=settings.is_development,  # Log SQL in development
            future=True,
            pool_pre_ping=True
        )
    
    return _async_engine

async def get_async_session_factory():
    """Get or create the async session factory."""
    global _async_session_factory
    
    if _async_session_factory is None:
        engine = await get_async_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    return _async_session_factory

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for dependency injection.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_database)):
            # Use db session here
            pass
    """
    session_factory = await get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all database tables."""
    # Import models to ensure they're registered
    from database import models
    
    engine = await get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all database tables (for testing)."""
    engine = await get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def create_sync_engine():
    """Create synchronous engine for migrations."""
    return create_engine(get_sync_database_url(), echo=settings.is_development)

async def close_database():
    """Close database connections."""
    global _async_engine, _async_session_factory
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        _async_session_factory = None

async def initialize_database():
    """Initialize the database with tables and default data."""
    await create_tables()
    
    # Create default admin user if it doesn't exist
    session_factory = await get_async_session_factory()
    async with session_factory() as session:
        from database.models import User
        from sqlalchemy import select
        
        # Check if admin user exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            # Create default admin user
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_user = User(
                username="admin",
                email="admin@localhost",
                password_hash=pwd_context.hash("admin"),
                full_name="Default Admin",
                is_admin=True,
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            print("Created default admin user (admin/admin)")

async def get_db_session() -> AsyncSession:
    """Get a database session outside of dependency injection."""
    session_factory = await get_async_session_factory()
    return session_factory()

# Health check function
async def check_database_health() -> dict:
    """Check database connectivity and return status."""
    try:
        session_factory = await get_async_session_factory()
        async with session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database_url": get_database_url().split("://")[0] + "://***",
                "connection": "active"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": get_database_url().split("://")[0] + "://***",
            "connection": "failed"
        }
