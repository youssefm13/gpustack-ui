from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.inference_client import send_to_gpustack, stream_from_gpustack
import json
from api.schemas import InferenceRequest, InferenceResponse, ErrorResponse

router = APIRouter()

@router.post("/infer", response_model=InferenceResponse, responses={500: {"model": ErrorResponse}})
async def infer(request: InferenceRequest) -> InferenceResponse:
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
        prompt_data = request.dict()
        
        # Log the request for debugging
        print(f"Inference request: {prompt_data}")
        
        result = await send_to_gpustack(prompt_data)
        
        # Log the response for debugging
        print(f"GPUStack response: {result}")
        
        return result
    except Exception as e:
        print(f"Inference error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream", responses={500: {"model": ErrorResponse}})
async def stream_infer(request: InferenceRequest):
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
        prompt_data = request.dict()
        prompt_data["stream"] = True
        
        print(f"Streaming inference request: {prompt_data}")
        
        async def generate():
            async for chunk in stream_from_gpustack(prompt_data):
                if chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        print(f"Streaming inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

