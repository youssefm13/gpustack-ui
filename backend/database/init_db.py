#!/usr/bin/env python3
"""
Database initialization script for GPUStack UI.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import initialize_database, check_database_health
from services.auth_service_enhanced import enhanced_auth_service


async def init_database():
    """Initialize the database with tables and default data."""
    print("🗄️  Initializing GPUStack UI database...")
    
    try:
        # Initialize database tables and default admin user
        await initialize_database()
        print("✅ Database initialized successfully!")
        
        # Check database health
        health = await check_database_health()
        print(f"📊 Database health: {health['status']}")
        print(f"🔗 Connection: {health['connection']}")
        
        # Clean up any expired sessions
        cleaned = await enhanced_auth_service.cleanup_expired_sessions()
        print(f"🧹 Cleaned up {cleaned} expired sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False


async def create_test_users():
    """Create additional test users for development."""
    print("👥 Creating test users...")
    
    try:
        # Create a regular test user
        await enhanced_auth_service.create_user(
            username="testuser",
            password="testpass",
            email="test@localhost",
            full_name="Test User",
            is_admin=False
        )
        print("✅ Created test user: testuser/testpass")
        
        # Create an admin test user
        await enhanced_auth_service.create_user(
            username="admin2",
            password="admin123",
            email="admin2@localhost",
            full_name="Admin User 2",
            is_admin=True
        )
        print("✅ Created admin user: admin2/admin123")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Test user creation failed (may already exist): {str(e)}")
        return False


async def main():
    """Main initialization function."""
    print("🚀 GPUStack UI Database Setup")
    print("=" * 40)
    
    # Initialize database
    if await init_database():
        print("\n🔧 Database setup completed successfully!")
        
        # Optionally create test users
        if len(sys.argv) > 1 and sys.argv[1] == "--test-users":
            print("\n👥 Setting up test users...")
            await create_test_users()
        
        print("\n📋 Available users:")
        print("   • admin/admin (default admin)")
        if len(sys.argv) > 1 and sys.argv[1] == "--test-users":
            print("   • testuser/testpass (regular user)")
            print("   • admin2/admin123 (admin user)")
        
        print("\n🎉 Ready to start the application!")
        
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
