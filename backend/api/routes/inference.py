from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated
from services.inference_client import send_to_gpustack, stream_from_gpustack
from middleware.auth_enhanced import get_current_user
from models.user import User
import json
from api.schemas import InferenceRequest, InferenceResponse, ErrorResponse
from api.routes.models import get_models, infer_model_metadata

router = APIRouter()

def validate_max_tokens(model_name: str, max_tokens: int) -> bool:
    """
    Dynamically validate max_tokens based on model capabilities.
    
    Args:
        model_name: Name of the model
        max_tokens: Requested max_tokens value
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Get model metadata to determine context window
        model_metadata = infer_model_metadata(model_name)
        context_window = model_metadata.get('n_ctx', 8192)  # Default fallback
        
        # Calculate safe maximum (80% of context window)
        safe_max = int(context_window * 0.8)
        
        # Allow up to 90% of context window for very large models (>100K context)
        if context_window > 100000:
            safe_max = int(context_window * 0.9)
        
        # Minimum reasonable limit
        min_limit = 100
        
        # Maximum reasonable limit (prevent abuse)
        max_limit = min(context_window, 500000)  # Cap at 500K for safety
        
        return min_limit <= max_tokens <= max_limit
        
    except Exception as e:
        # Fallback to conservative limits
        return 100 <= max_tokens <= 32768

@router.post("/infer", response_model=InferenceResponse, responses={500: {"model": ErrorResponse}})
async def infer(
    request: InferenceRequest,
    current_user: Annotated[User, Depends(get_current_user)]
) -> InferenceResponse:
    """
    Generate text completion using LLM models.
    
    Send a chat completion request to the GPUStack LLM server and return the generated response.
    Supports various parameters for controlling the generation process.
    
    - **model**: The model ID to use for generation
    - **messages**: List of chat messages in OpenAI format
    - **temperature**: Controls randomness (0.0 = deterministic, 2.0 = very random)
    - **max_tokens**: Maximum number of tokens to generate
    - **stream**: Whether to stream the response (use /stream endpoint for streaming)
    """
    try:
        # Convert Pydantic model to dict
        prompt_data = request.model_dump()
        
        # Validate max_tokens dynamically based on model capabilities
        model_name = prompt_data.get('model')
        max_tokens = prompt_data.get('max_tokens', 4000)
        
        if not validate_max_tokens(model_name, max_tokens):
            model_metadata = infer_model_metadata(model_name)
            context_window = model_metadata.get('n_ctx', 8192)
            safe_max = int(context_window * 0.8)
            if context_window > 100000:
                safe_max = int(context_window * 0.9)
            
            raise HTTPException(
                status_code=422, 
                detail=f"max_tokens ({max_tokens}) exceeds safe limit for model {model_name}. "
                       f"Context window: {context_window}, Safe maximum: {safe_max}"
            )
        
        result = await send_to_gpustack(prompt_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream", responses={500: {"model": ErrorResponse}})
async def stream_infer(
    request: InferenceRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):

    """
    Generate streaming text completion using LLM models.
    
    Send a chat completion request to the GPUStack LLM server and stream the response back
    in real-time. This endpoint returns Server-Sent Events (SSE) for real-time streaming.
    
    The response format follows OpenAI's streaming format with 'data:' prefixed JSON chunks.
    The stream ends with 'data: [DONE]'.
    
    Parameters are the same as the /infer endpoint, but streaming is automatically enabled.
    """

    
    try:
        # Convert Pydantic model to dict and enable streaming
        prompt_data = request.model_dump()
        prompt_data["stream"] = True
        
        # Validate max_tokens dynamically based on model capabilities
        model_name = prompt_data.get('model')
        max_tokens = prompt_data.get('max_tokens', 4000)
        
        if not validate_max_tokens(model_name, max_tokens):
            model_metadata = infer_model_metadata(model_name)
            context_window = model_metadata.get('n_ctx', 8192)
            safe_max = int(context_window * 0.8)
            if context_window > 100000:
                safe_max = int(context_window * 0.9)
            
            raise HTTPException(
                status_code=422, 
                detail=f"max_tokens ({max_tokens}) exceeds safe limit for model {model_name}. "
                       f"Context window: {context_window}, Safe maximum: {safe_max}"
            )
        

        
        async def generate():
            async for chunk in stream_from_gpustack(prompt_data):
                if chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

