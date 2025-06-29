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
            
            print(f"GPUStack status code: {res.status_code}")
            
            if res.status_code != 200:
                print(f"GPUStack error response: {res.text}")
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
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream('POST', f"{settings.gpustack_api_base}/v1/chat/completions", json=data, headers=headers) as response:
                
                print(f"GPUStack streaming status code: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"GPUStack streaming error: {error_text}")
                    response.raise_for_status()
                
                buffer = ""
                async for chunk in response.aiter_text():
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
                                except json.JSONDecodeError:
                                    continue
                                    
    except httpx.TimeoutException:
        raise Exception("Streaming request to GPUStack timed out")
    except httpx.HTTPStatusError as e:
        raise Exception(f"GPUStack streaming HTTP error: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"GPUStack streaming connection error: {str(e)}")

