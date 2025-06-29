from fastapi import APIRouter, Depends, HTTPException, Request
from config.settings import settings
import httpx
import re
from typing import Dict, Any
from api.schemas import ModelsResponse, ErrorResponse

router = APIRouter()

@router.get("", response_model=ModelsResponse, responses={500: {"model": ErrorResponse}})
async def get_models(request: Request) -> ModelsResponse:
    """
    Retrieve available LLM models from GPUStack server.
    
    This endpoint fetches all available language models from the connected GPUStack instance.
    Only LLM models are returned (filtering out image, embedding, and reranker models).
    
    Returns:
        ModelsResponse: List of available models with their metadata
        
    Raises:
        HTTPException: If the GPUStack server is unreachable or returns an error
    """
    try:
        # Construct the models endpoint URL
        models_url = f"{settings.gpustack_api_base}/v1/models"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if settings.gpustack_api_token:
            headers["Authorization"] = f"Bearer {settings.gpustack_api_token}"
        
        # Use shared HTTP client from app state  
        http_client = request.app.state.http_client
        response = await http_client.get(models_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter LLM models and add enhanced status information
            llm_models = []
            if 'items' in data:
                for model in data['items']:
                    # Include only LLM models (exclude image, embedding, reranker)
                    if 'llm' in model.get('categories', []):
                        try:
                            # Add enhanced model info with status checks
                            model = await enhance_model_info(model, http_client, headers)
                        except Exception as e:
                            # Fallback to basic model info if enhancement fails
                            model = add_basic_model_info(model)
                        llm_models.append(model)
            
            return {"models": llm_models}
        else:
            raise HTTPException(status_code=response.status_code, 
                              detail=f"GPUStack API error: {response.text}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

def add_basic_model_info(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add basic model information without status checks.
    """
    # Infer model capabilities from name
    model["meta"] = infer_model_metadata(model["name"])
    model["status"] = "unknown"  # We'll add status checks later
    model["ready_replicas"] = 1  # Assume ready for now
    model["total_replicas"] = 1
    model["status_description"] = "Status check disabled for performance"
    model["last_updated"] = model.get("created_at", "")
    
    # Add UI-friendly display info
    model["display_name"] = create_display_name(model["name"], model["meta"])
    model["size_category"] = categorize_model_size(model["meta"].get("n_params", 0))
    
    return model

async def enhance_model_info(model: Dict[str, Any], http_client: httpx.AsyncClient, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Enhance model info with status checks and inferred capabilities.
    """
    try:
        # Test if model is responsive by making a simple chat completions call
        test_url = f"{settings.gpustack_api_base}/v1/chat/completions"
        test_payload = {
            "model": model["name"],
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 1,
            "temperature": 0.0
        }
        
        try:
            test_response = await http_client.post(
                test_url, 
                headers=headers, 
                json=test_payload,
                timeout=10.0
            )
            
            if test_response.status_code == 200:
                model["status"] = "ready"
                model["ready_replicas"] = 1
                model["status_description"] = "Model is online and ready to serve requests"
            else:
                model["status"] = "error"
                model["ready_replicas"] = 0
                model["status_description"] = f"Model error: {test_response.status_code}"
                
        except Exception as test_error:
            # If test call fails, model might be loading or offline
            model["status"] = "loading"
            model["ready_replicas"] = 0
            model["status_description"] = "Model may be loading or temporarily unavailable"
            print(f"Model {model['name']} test failed: {str(test_error)}")
        
        # Infer model capabilities from name
        model["meta"] = infer_model_metadata(model["name"])
        model["total_replicas"] = 1
        model["last_updated"] = model.get("created_at", "")
        
        # Add UI-friendly display info
        model["display_name"] = create_display_name(model["name"], model["meta"])
        model["size_category"] = categorize_model_size(model["meta"].get("n_params", 0))
        
    except Exception as e:
        # If all fails, mark as unknown but don't crash
        print(f"Error enhancing model info for {model['name']}: {str(e)}")
        model["status"] = "unknown"
        model["ready_replicas"] = 0
        model["meta"] = {"n_ctx": 8192, "n_params": 0}
        model["status_description"] = "Status unknown - unable to verify model availability"
        model["display_name"] = model["name"]
        model["size_category"] = "unknown"
    
    return model

def infer_model_metadata(model_name: str) -> Dict[str, Any]:
    """
    Infer model metadata based on naming conventions.
    """
    name_lower = model_name.lower()
    
    # Common parameter sizes based on model names
    param_patterns = {
        r'(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,  # 7b -> 7 billion
        r'(\d+)m': lambda m: int(m.group(1)) * 1_000_000,      # 500m -> 500 million
        r'qwen.*3.*32': lambda m: 32_000_000_000,              # qwen3-32b
        r'qwen.*3.*235': lambda m: 235_000_000_000,            # qwen3-235b
        r'qwen.*3': lambda m: 7_000_000_000,                   # qwen3 default
        r'llama.*4.*17': lambda m: 17_000_000_000,             # llama-4-17b
        r'deepseek': lambda m: 7_000_000_000,                  # deepseek default
    }
    
    # Context window patterns
    context_patterns = {
        r'qwen.*3.*32': 32768,
        r'qwen.*3.*235': 131072,
        r'qwen.*3': 32768,
        r'llama.*4': 32768,
        r'deepseek': 32768,
    }
    
    n_params = 0
    n_ctx = 8192  # default
    
    # Match parameter count
    for pattern, extractor in param_patterns.items():
        match = re.search(pattern, name_lower)
        if match:
            if callable(extractor):
                n_params = extractor(match)
            else:
                n_params = extractor
            break
    
    # Match context window
    for pattern, ctx in context_patterns.items():
        if re.search(pattern, name_lower):
            n_ctx = ctx
            break
    
    return {
        "n_params": n_params,
        "n_ctx": n_ctx,
        "architecture": infer_architecture(name_lower),
        "quantization": infer_quantization(name_lower),
        "precision": infer_precision(name_lower)
    }

def infer_architecture(name_lower: str) -> str:
    """Infer model architecture from name."""
    if 'qwen' in name_lower:
        return 'qwen'
    elif 'llama' in name_lower:
        return 'llama'
    elif 'deepseek' in name_lower:
        return 'deepseek'
    else:
        return 'unknown'

def infer_quantization(name_lower: str) -> str:
    """Infer quantization type from name."""
    if 'q8_0' in name_lower or 'q8' in name_lower:
        return 'Q8_0'
    elif 'q4' in name_lower:
        return 'Q4_0'
    elif 'bf16' in name_lower:
        return 'BF16'
    elif 'f16' in name_lower:
        return 'F16'
    else:
        return 'unknown'

def infer_precision(name_lower: str) -> str:
    """Infer precision from name."""
    if 'bf16' in name_lower:
        return 'bfloat16'
    elif 'f16' in name_lower:
        return 'float16'
    elif 'f32' in name_lower:
        return 'float32'
    else:
        return 'mixed'

def create_display_name(name: str, meta: Dict[str, Any]) -> str:
    """Create a user-friendly display name."""
    params = meta.get('n_params', 0)
    if params > 0:
        if params >= 1_000_000_000:
            size_str = f"({params / 1_000_000_000:.1f}B)"
        else:
            size_str = f"({params / 1_000_000:.0f}M)"
        return f"{name} {size_str}"
    return name

def categorize_model_size(params: int) -> str:
    """Categorize model by parameter count."""
    if params == 0:
        return "unknown"
    elif params < 1_000_000_000:  # < 1B
        return "small"
    elif params < 10_000_000_000:  # < 10B
        return "medium"
    elif params < 50_000_000_000:  # < 50B
        return "large"
    else:
        return "extra-large"
