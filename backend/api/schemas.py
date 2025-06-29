"""
API Schema Models for GPUStack UI Backend

This module contains Pydantic models that define the structure of API requests and responses.
These models are used for automatic OpenAPI documentation generation and request validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Common response models
class BaseResponse(BaseModel):
    """Base response model with common fields."""
    status: str = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Optional message")

class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field("error", description="Error status")
    detail: str = Field(..., description="Error details")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")

# Health and Metrics Models
class SystemMetrics(BaseModel):
    """System performance metrics."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_available_mb: int = Field(..., description="Available memory in MB")

class PerformanceMetrics(BaseModel):
    """Performance metrics."""
    requests_per_minute: float = Field(..., description="Average requests per minute")
    avg_concurrent_users: float = Field(..., description="Average concurrent users")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    uptime_seconds: int = Field(..., description="Service uptime in seconds")
    active_connections: int = Field(..., description="Current active connections")
    total_requests: int = Field(..., description="Total requests since startup")
    system: SystemMetrics = Field(..., description="System performance metrics")
    performance: PerformanceMetrics = Field(..., description="Performance metrics")

class EstimatedCapacity(BaseModel):
    """Estimated capacity under different usage scenarios."""
    light_usage: str = Field(..., description="Capacity under light usage")
    medium_usage: str = Field(..., description="Capacity under medium usage")
    heavy_usage: str = Field(..., description="Capacity under heavy usage")

class DetailedMetricsResponse(BaseModel):
    """Detailed performance metrics response."""
    concurrent_connections: int = Field(..., description="Current concurrent connections")
    total_requests: int = Field(..., description="Total requests processed")
    uptime_hours: float = Field(..., description="Service uptime in hours")
    requests_per_hour: float = Field(..., description="Average requests per hour")
    estimated_capacity: EstimatedCapacity = Field(..., description="Estimated user capacity")

# Models API Models
class ModelMetadata(BaseModel):
    """Model metadata and capabilities."""
    n_params: int = Field(..., description="Number of parameters")
    n_ctx: int = Field(..., description="Context window size")
    architecture: str = Field(..., description="Model architecture")
    quantization: str = Field(..., description="Quantization type")
    precision: str = Field(..., description="Precision type")

class ModelItem(BaseModel):
    """Individual model information with enhanced status and metadata."""
    id: Union[str, int] = Field(..., description="Model identifier")
    name: str = Field(..., description="Model name")
    categories: List[str] = Field(..., description="Model categories (e.g., ['llm'])")
    description: Optional[str] = Field(None, description="Model description")
    created_at: Optional[datetime] = Field(None, description="Model creation date")
    
    # Enhanced fields
    status: str = Field(..., description="Model status (ready, loading, error, unknown)")
    display_name: str = Field(..., description="User-friendly display name")
    ready_replicas: int = Field(..., description="Number of ready replicas")
    total_replicas: int = Field(..., description="Total number of replicas")
    status_description: str = Field(..., description="Detailed status description")
    last_updated: str = Field(..., description="Last updated timestamp")
    size_category: str = Field(..., description="Model size category (small, medium, large, etc.)")
    meta: ModelMetadata = Field(..., description="Model metadata and capabilities")

class ModelsResponse(BaseModel):
    """Response containing available models."""
    models: List[ModelItem] = Field(..., description="List of available LLM models")

# Inference API Models
class InferenceRequest(BaseModel):
    """Inference request model."""
    model: str = Field(..., description="Model ID to use for inference", example="qwen3")
    messages: List[Dict[str, str]] = Field(
        ..., 
        description="List of messages in chat format",
        example=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(1000, gt=0, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="Presence penalty")
    repetition_penalty: Optional[float] = Field(1.1, ge=0.0, le=2.0, description="Repetition penalty")

class InferenceChoice(BaseModel):
    """Individual inference choice."""
    index: int = Field(..., description="Choice index")
    message: Dict[str, str] = Field(..., description="Generated message")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing")

class InferenceUsage(BaseModel):
    """Token usage information."""
    model_config = ConfigDict(extra="allow")  # Allow additional fields from GPUStack
    
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    completion_tokens: int = Field(..., description="Tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens used")

class InferenceResponse(BaseModel):
    """Inference response model."""
    id: str = Field(..., description="Response ID")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[InferenceChoice] = Field(..., description="Generated choices")
    usage: InferenceUsage = Field(..., description="Token usage information")

# Search API Models
class SearchRequest(BaseModel):
    """Web search request model."""
    q: str = Field(..., description="Search query", example="latest developments in AI")

class SearchResult(BaseModel):
    """Individual search result."""
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    content: str = Field(..., description="Result content")
    score: float = Field(..., description="Relevance score")
    published_date: str = Field(..., description="Publication date")
    index: int = Field(..., description="Result index")

class SearchResultData(BaseModel):
    """Search result data structure."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="List of search results")
    llm_summary: Optional[str] = Field(None, description="LLM-processed summary")
    processing_status: Optional[str] = Field(None, description="Processing status")
    processing_error: Optional[str] = Field(None, description="Processing error if any")

class SearchResponse(BaseModel):
    """Web search response model."""
    result: SearchResultData = Field(..., description="Search results with AI-processed summary")

# File Upload Models
class FileMetadata(BaseModel):
    """File metadata information."""
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs)")
    word_count: Optional[int] = Field(None, description="Estimated word count")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class StructureInfo(BaseModel):
    """File structure information."""
    has_headers: bool = Field(..., description="Whether the file contains headers")
    has_tables: bool = Field(..., description="Whether the file contains tables")
    page_count: Optional[int] = Field(None, description="Number of pages")
    word_count: Optional[int] = Field(None, description="Word count")

class FileUploadResponse(BaseModel):
    """File upload response model."""
    content: str = Field(..., description="Processed file content")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    metadata: FileMetadata = Field(..., description="File metadata")
    structure_info: StructureInfo = Field(..., description="File structure information")
    processing_status: str = Field(..., description="Processing status (success/error)")
    processing_notes: List[str] = Field(..., description="Processing notes and optimizations applied")

class LegacyFileUploadResponse(BaseModel):
    """Legacy file upload response for backward compatibility."""
    content: str = Field(..., description="Processed file content")

# Root endpoint model
class RootResponse(BaseModel):
    """Root endpoint response."""
    message: str = Field(..., description="Welcome message")
