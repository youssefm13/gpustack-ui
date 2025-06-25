from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import files, tools, inference, models

app = FastAPI(title="GPUStack UI Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"])
app.include_router(models.router, prefix="/api/models", tags=["models"])

@app.get("/")
def read_root():
    return {"message": "GPUStack UI Backend Running"}

