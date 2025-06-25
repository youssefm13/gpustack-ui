# GPUStack UI Performance Optimization Guide

## Current Bottlenecks Analysis

### 1. **Backend Concurrency (Primary Bottleneck)**
- Single uvicorn worker
- No async optimization for external calls
- Blocking operations during file processing and search

### 2. **External API Dependencies**
- GPUStack inference queue
- Tavily search API rate limits
- File processing blocking operations

## Immediate Improvements (Easy to implement)

### 1. **Scale Uvicorn Workers**
```yaml
# In docker-compose.yml, update backend command:
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### 2. **Add Connection Pooling**
```python
# Add to backend/main.py
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create HTTP client pool
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        timeout=30.0
    )
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

### 3. **Async Search Operations**
```python
# Convert search operations to async
async def perform_web_search_async(query: str):
    # Use app.state.http_client for async requests
    # This prevents blocking the event loop
```

## Medium-term Improvements

### 1. **Request Queuing System**
```python
# Add Redis for request queuing
from celery import Celery

# Queue heavy operations (search, file processing)
# Return immediately with task ID
# Poll for results asynchronously
```

### 2. **Caching Layer**
```python
# Cache search results and LLM responses
from functools import lru_cache
import redis

# Cache search results for 1 hour
# Cache LLM responses for similar queries
```

### 3. **Load Balancer Setup**
```yaml
# Add nginx load balancer
# Multiple backend instances
# Session affinity for WebSocket connections
```

## Advanced Scaling (High-concurrency)

### 1. **Microservices Architecture**
- Separate search service
- Separate file processing service
- Separate inference proxy service

### 2. **Auto-scaling**
```yaml
# Kubernetes deployment with HPA
# Scale based on CPU/memory usage
# Separate scaling for different services
```

### 3. **Database Integration**
```python
# PostgreSQL for user sessions
# Redis for caching and queuing
# Async database operations
```

## Expected Improvements

| Optimization Level | Concurrent Users | Implementation Effort |
|-------------------|------------------|---------------------|
| Current          | 20-50            | None                |
| Basic (Workers)  | 100-200          | 1 hour              |
| Medium (Async)   | 500-1000         | 1-2 days            |
| Advanced (Queue) | 2000-5000        | 1-2 weeks           |
| Enterprise      | 10000+           | 1-2 months          |

## Quick Implementation

For immediate improvement, update your docker-compose.yml:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - GPUSTACK_API_URL=${GPUSTACK_API_URL}
      - GPUSTACK_API_KEY=${GPUSTACK_API_KEY}
    volumes:
      - ./backend:/app
    deploy:
      replicas: 3  # Multiple backend instances
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

  nginx:
    image: nginx:alpine
    ports:
      - "3000:80"
      - "8001:8001"
    volumes:
      - ./frontend/public:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
```

This would increase capacity to ~200-500 concurrent users with minimal effort.
