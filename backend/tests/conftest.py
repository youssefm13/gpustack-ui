"""
Test configuration and fixtures for GPUStack UI backend.
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment
os.environ["TESTING"] = "1"
os.environ["GPUSTACK_API_BASE"] = "http://localhost:8080"
os.environ["GPUSTACK_API_TOKEN"] = "test-gpustack-token"
os.environ["TAVILY_API_KEY"] = "test-key"

from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def mock_gpustack_response():
    """Mock response data for GPUStack API calls."""
    return {
        "models": [
            {
                "id": 1,
                "name": "qwen-test",
                "meta": {
                    "n_ctx": 8192,
                    "n_params": 7000000000
                },
                "ready_replicas": 1
            }
        ]
    }


@pytest.fixture
def mock_user_data():
    """Mock user data for authentication tests."""
    from models.user import User
    from datetime import datetime, timezone
    return User(
        id=1,
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        is_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def auth_headers(mock_user_data):
    """Create authentication headers for testing."""
    from services.auth_service_enhanced import enhanced_auth_service
    
    token = enhanced_auth_service.create_access_token_sync(mock_user_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_file_content():
    """Sample file content for file processing tests."""
    return {
        "pdf": b"%PDF-1.4 test content",
        "txt": "This is a test document content.",
        "docx": b"PK\x03\x04 test docx content"
    }


@pytest.fixture
def mock_tavily_response():
    """Mock response from Tavily search API."""
    return {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "snippet": "This is a test search result",
                "content": "Full content of test result 1"
            },
            {
                "title": "Test Result 2", 
                "url": "https://example.com/2",
                "snippet": "Another test search result",
                "content": "Full content of test result 2"
            }
        ]
    }
