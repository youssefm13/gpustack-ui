# GPUStack UI Backend API Documentation

This document provides comprehensive information about the GPUStack UI Backend API, including interactive documentation, schemas, and usage examples.

## 📚 Interactive Documentation

The API provides **automatic interactive documentation** through Swagger UI and ReDoc:

### Swagger UI (Recommended)
- **URL**: `http://localhost:8001/docs`
- **Features**: 
  - Interactive endpoint testing
  - Request/response examples
  - Schema validation
  - Built-in "Try it out" functionality

### ReDoc (Alternative)
- **URL**: `http://localhost:8001/redoc`
- **Features**:
  - Clean, readable documentation
  - Mobile-friendly interface
  - Better for reading-only documentation

### OpenAPI Schema
- **URL**: `http://localhost:8001/openapi.json`
- **Format**: JSON schema following OpenAPI 3.1.0 specification
- **Usage**: Import into API clients, generate SDKs, or integrate with tools

## 🏗️ API Overview

### Base Information
- **Title**: GPUStack UI Backend API
- **Version**: 2.1.0-dev
- **Base URL**: `http://localhost:8001`
- **License**: MIT

### Core Features
- **LLM Inference**: Chat with various language models
- **File Processing**: Upload and process documents (PDF, TXT, etc.)
- **Web Search**: AI-enhanced web search with smart summaries
- **Model Management**: List and manage available models
- **Health Monitoring**: System health and performance metrics

## 📋 Endpoint Categories

### 🏥 Health & Monitoring
- `GET /api/health` - Comprehensive health check with system metrics
- `GET /api/metrics` - Detailed performance and capacity metrics

### 🤖 Model Management
- `GET /api/models` - List available LLM models from GPUStack

### 💬 LLM Inference
- `POST /api/inference/infer` - Generate text completion (non-streaming)
- `POST /api/inference/stream` - Generate streaming text completion

### 🔍 Tools & Search
- `POST /api/tools/search` - AI-enhanced web search with summaries

### 📄 File Processing
- `POST /api/files/upload` - Enhanced file upload with metadata
- `POST /api/files/upload/legacy` - Legacy file upload (backward compatibility)

### 🏠 Utility
- `GET /` - Root endpoint with API information

## 🔧 Request/Response Models

All endpoints use **Pydantic models** for request validation and response serialization:

### Key Features:
- **Automatic validation** of request parameters
- **Type checking** and error messages
- **Consistent error responses** across all endpoints
- **Rich metadata** including descriptions and examples

### Common Response Types:
- **Success responses**: Endpoint-specific schemas
- **Error responses**: Structured error format with HTTP status codes
- **Validation errors**: Detailed field-level error information

## 🚀 Usage Examples

### Health Check
```bash
curl -X GET "http://localhost:8001/api/health"
```

### LLM Inference
```bash
curl -X POST "http://localhost:8001/api/inference/infer" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instruct",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### Web Search
```bash
curl -X POST "http://localhost:8001/api/tools/search" \
  -H "Content-Type: application/json" \
  -d '{"q": "latest developments in AI"}'
```

### File Upload
```bash
curl -X POST "http://localhost:8001/api/files/upload" \
  -F "file=@document.pdf"
```

## 📊 API Features

### 🔄 Request Validation
- **Pydantic models** ensure type safety and validation
- **Field constraints** (min/max values, string patterns)
- **Detailed error messages** for invalid requests

### 📈 Performance Monitoring
- **Built-in metrics** tracking active connections and request counts
- **System metrics** including CPU and memory usage
- **Capacity estimates** for different usage scenarios

### 🔒 Error Handling
- **Structured error responses** following consistent format
- **HTTP status codes** appropriate to error types
- **Detailed error messages** for debugging

### 🌊 Streaming Support
- **Server-Sent Events (SSE)** for real-time streaming
- **OpenAI-compatible** streaming format
- **Graceful connection handling** and cleanup

## 🛠️ Development Features

### Schema Generation
- **Automatic OpenAPI schema** generation from code
- **Rich descriptions** and examples in endpoint documentation
- **Type annotations** for better IDE support

### Testing Support
- **Interactive testing** through Swagger UI
- **Request examples** for each endpoint
- **Response schemas** for validation

### Integration Ready
- **OpenAPI 3.1.0** compatible schema
- **SDK generation** support for multiple languages
- **API client** integration ready

## 📝 Schema Highlights

### Request Models
- `InferenceRequest` - LLM inference parameters with validation
- `SearchRequest` - Web search query validation
- File upload handling with multipart/form-data

### Response Models
- `HealthResponse` - Comprehensive health and metrics data
- `ModelsResponse` - Available models with metadata
- `InferenceResponse` - LLM completion results
- `FileUploadResponse` - Enhanced file processing results

### Error Models
- `ErrorResponse` - Consistent error format across all endpoints
- `HTTPValidationError` - Detailed validation error information

## 🔧 Configuration

### Environment Variables
The API documentation respects environment-based configuration for:
- GPUStack server connection details
- API keys and authentication
- Performance and timeout settings

### CORS Support
- **Configurable origins** for cross-origin requests
- **Development-friendly** defaults
- **Production-ready** security options

## 📈 Performance Considerations

### Current Capacity
- **100-200 concurrent users** under normal load
- **Connection pooling** for efficient resource usage
- **Async architecture** for high concurrency

### Monitoring
- Real-time metrics through `/api/health` and `/api/metrics`
- Connection tracking and request counting
- System resource monitoring

---

## 🚀 Getting Started

1. **Start the backend**: `docker-compose up backend`
2. **Visit Swagger UI**: http://localhost:8001/docs
3. **Explore endpoints**: Use the interactive interface to test APIs
4. **Check health**: `curl http://localhost:8001/api/health`

For more detailed setup instructions, see the main [README.md](../README.md).
