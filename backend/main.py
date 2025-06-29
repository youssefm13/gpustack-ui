from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from api.routes import files, tools, inference, models, health, auth
from api.routes.health import track_connections_middleware
from middleware.auth import JWTMiddleware
from api import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create shared HTTP client with connection pooling
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_keepalive_connections=50,
            max_connections=200,
            keepalive_expiry=30
        ),
        timeout=httpx.Timeout(30.0, connect=10.0)
    )
    print("✅ HTTP client pool initialized")
    yield
    await app.state.http_client.aclose()
    print("🔌 HTTP client pool closed")

app = FastAPI(
    title="GPUStack UI Backend API",
    description="""
    A comprehensive backend API for the GPUStack UI application.
    
    This API provides endpoints for:
    - **LLM Inference**: Chat with various language models
    - **File Processing**: Upload and process documents (PDF, TXT, etc.)
    - **Web Search**: AI-enhanced web search with smart summaries
    - **Model Management**: List and manage available models
    - **Health Monitoring**: System health and performance metrics
    
    ## Authentication
    Currently, no authentication is required for API access.
    
    ## Rate Limiting
    The API supports concurrent requests with connection pooling.
    Current capacity: ~100-200 concurrent users under normal load.
    
    ## Error Handling
    All endpoints return structured error responses with appropriate HTTP status codes.
    """,
    version="2.1.0-dev",
    contact={
        "name": "GPUStack UI Team",
        "url": "https://github.com/youssefm13/gpustack-ui",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and performance monitoring endpoints"
        },
        {
            "name": "models", 
            "description": "Model management and discovery endpoints"
        },
        {
            "name": "inference",
            "description": "LLM inference endpoints for chat and completion"
        },
        {
            "name": "tools",
            "description": "Tool endpoints including web search functionality"
        },
        {
            "name": "files",
            "description": "File upload and processing endpoints"
        },
        {
            "name": "auth",
            "description": "Authentication endpoints for user login and session management"
        }
    ],
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add connection tracking middleware
app.middleware("http")(track_connections_middleware)

# Add JWT middleware
app.add_middleware(JWTMiddleware)

app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/", response_model=schemas.RootResponse, tags=["root"])
def read_root() -> schemas.RootResponse:
    """
    Root endpoint providing API information.
    
    Returns basic information about the API service status.
    Visit /docs for interactive API documentation.
    """
    return {"message": "GPUStack UI Backend Running"}

