from fastapi import APIRouter, HTTPException
import httpx
from config import GPUSTACK_API_URL, GPUSTACK_API_KEY

router = APIRouter()

@router.get("", response_model=None)
async def get_models():
    """Fetch available models from GPUStack server"""
    try:
        # Construct the models endpoint URL
        base_url = GPUSTACK_API_URL.replace('/v1/chat/completions', '')
        models_url = f"{base_url}/v1/models"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if GPUSTACK_API_KEY:
            headers["Authorization"] = f"Bearer {GPUSTACK_API_KEY}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(models_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter for LLM models only (exclude image, embedding, reranker models)
                llm_models = []
                if 'items' in data:
                    for model in data['items']:
                        # Include only LLM models (exclude image, embedding, reranker)
                        if 'llm' in model.get('categories', []):
                            llm_models.append(model)
                
                return {"models": llm_models}
            else:
                raise HTTPException(status_code=response.status_code, 
                                  detail=f"GPUStack API error: {response.text}")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to GPUStack timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, 
                          detail=f"GPUStack HTTP error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")
