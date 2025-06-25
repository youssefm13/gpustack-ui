from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.inference_client import send_to_gpustack, stream_from_gpustack
import json

router = APIRouter()

@router.post("/infer")
async def infer(prompt_data: dict):
    try:
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

@router.post("/stream")
async def stream_infer(prompt_data: dict):
    try:
        # Add streaming parameter to the request
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

