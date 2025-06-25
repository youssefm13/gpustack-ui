from fastapi import APIRouter, Request
from datetime import datetime
import psutil
import asyncio

router = APIRouter()

# Simple in-memory counter for active connections
active_connections = 0
total_requests = 0
start_time = datetime.now()

# This middleware function will be added to the main app in main.py
async def track_connections_middleware(request: Request, call_next):
    global active_connections, total_requests
    
    active_connections += 1
    total_requests += 1
    
    try:
        response = await call_next(request)
        return response
    finally:
        active_connections -= 1

@router.get("/health")
async def health_check():
    """Health check endpoint with performance metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        uptime = datetime.now() - start_time
        
        return {
            "status": "healthy",
            "uptime_seconds": int(uptime.total_seconds()),
            "active_connections": active_connections,
            "total_requests": total_requests,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024)
            },
            "performance": {
                "requests_per_minute": total_requests / max(uptime.total_seconds() / 60, 1),
                "avg_concurrent_users": total_requests / max(uptime.total_seconds(), 1)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "active_connections": active_connections,
            "total_requests": total_requests
        }

@router.get("/metrics")
async def performance_metrics():
    """Detailed performance metrics"""
    uptime = datetime.now() - start_time
    
    return {
        "concurrent_connections": active_connections,
        "total_requests": total_requests,
        "uptime_hours": uptime.total_seconds() / 3600,
        "requests_per_hour": total_requests / max(uptime.total_seconds() / 3600, 1),
        "estimated_capacity": {
            "light_usage": "100-200 users",
            "medium_usage": "50-100 users", 
            "heavy_usage": "20-50 users"
        }
    }
