import httpx
import json
from config.settings import settings
from typing import Dict, Any, AsyncGenerator

async def send_to_gpustack(data):
    headers = {
        "Content-Type": "application/json"
    }
    
    if settings.gpustack_api_token:
        headers["Authorization"] = f"Bearer {settings.gpustack_api_token}"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(f"{settings.gpustack_api_base}/v1/chat/completions", json=data, headers=headers)
            
            if res.status_code != 200:
                res.raise_for_status()
            
            return res.json()
    except httpx.TimeoutException:
        raise Exception("Request to GPUStack timed out")
    except httpx.HTTPStatusError as e:
        raise Exception(f"GPUStack HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise Exception(f"GPUStack connection error: {str(e)}")

async def stream_from_gpustack(data):
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    if settings.gpustack_api_token:
        headers["Authorization"] = f"Bearer {settings.gpustack_api_token}"
    
    try:
        # Use longer timeout for very large models (100B+ parameters)
        timeout_seconds = 300.0 if any("235b" in data.get("model", "").lower() for _ in [1]) else 120.0
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            async with client.stream('POST', f"{settings.gpustack_api_base}/v1/chat/completions", json=data, headers=headers) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    response.raise_for_status()
                
                buffer = ""
                chunk_count = 0
                async for chunk in response.aiter_text():
                    chunk_count += 1
                    buffer += chunk
                    
                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        
                        if line.startswith("data: "):
                            data_content = line[6:].strip()
                            if data_content == "[DONE]":
                                return
                            
                            if data_content:
                                try:
                                    chunk_data = json.loads(data_content)
                                    yield chunk_data
                                except json.JSONDecodeError as e:
                                    continue
                                    
    except httpx.TimeoutException:
        raise Exception("Streaming request to GPUStack timed out")
    except httpx.HTTPStatusError as e:
        error_msg = f"GPUStack streaming HTTP error: {e.response.status_code}"
        if e.response.status_code == 404:
            error_msg += " - Model not found or not available"
        elif e.response.status_code == 400:
            error_msg += " - Bad request (check model parameters)"
        elif e.response.status_code == 401:
            error_msg += " - Unauthorized (check API token)"
        elif e.response.status_code == 429:
            error_msg += " - Rate limited (too many requests)"
        elif e.response.status_code == 503:
            error_msg += " - Service unavailable (model may be loading or overloaded)"
        elif e.response.status_code == 422:
            error_msg += " - Unprocessable entity (check request format)"
        try:
            error_detail = await e.response.aread()
            error_msg += f" - {error_detail.decode()}"
        except:
            pass
        raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"GPUStack streaming connection error: {str(e)}")

