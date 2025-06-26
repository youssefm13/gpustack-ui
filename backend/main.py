from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from api.routes import files, tools, inference, models, health
from api.routes.health import track_connections_middleware

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
    title="GPUStack UI Backend",
    version="1.1.0-performance",
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

app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(health.router, prefix="/api", tags=["health"])

@app.get("/")
def read_root():
    return {"message": "GPUStack UI Backend Running"}

