#!/usr/bin/env python3
"""
Simple database test script.
"""

import asyncio
import sys
import os

from database.connection import initialize_database, check_database_health

async def main():
    print("🗄️  Testing database initialization...")
    
    try:
        await initialize_database()
        print("✅ Database initialized successfully!")
        
        health = await check_database_health()
        print(f"📊 Database health: {health}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
