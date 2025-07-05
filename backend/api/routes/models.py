from fastapi import APIRouter, HTTPException, Request
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
        # Infer model capabilities from name first
        model["meta"] = infer_model_metadata(model["name"])
        
        # For very large models (100B+ parameters), skip testing and assume ready
        # These models can take a very long time to respond to test calls
        if model["meta"].get("n_params", 0) > 100_000_000_000:  # 100B+ parameters
    
            model["status"] = "ready"
            model["ready_replicas"] = 1
            model["status_description"] = "Large model - assumed ready (test skipped for performance)"
        else:
            # Test if model is responsive by making a simple chat completions call
            test_url = f"{settings.gpustack_api_base}/v1/chat/completions"
            test_payload = {
                "model": model["name"],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10,  # Increased from 1 for better model testing
                "temperature": 0.0
            }
            
    
            
            try:
                test_response = await http_client.post(
                    test_url, 
                    headers=headers, 
                    json=test_payload,
                    timeout=15.0  # Increased timeout for large models
                )
                
                if test_response.status_code == 200:
                    model["status"] = "ready"
                    model["ready_replicas"] = 1
                    model["status_description"] = "Model is online and ready to serve requests"
                else:
                    response_text = test_response.text[:200]  # Limit response text for logging
                    model["status"] = "error"
                    model["ready_replicas"] = 0
                    model["status_description"] = f"Model error: {test_response.status_code} - {response_text}"
                    
            except Exception as test_error:
                # If test call fails, model might be loading or offline
                model["status"] = "loading"
                model["ready_replicas"] = 0
                model["status_description"] = f"Model may be loading or temporarily unavailable: {str(test_error)}"
        
        model["total_replicas"] = 1
        model["last_updated"] = model.get("created_at", "")
        
        # Add UI-friendly display info
        model["display_name"] = create_display_name(model["name"], model["meta"])
        model["size_category"] = categorize_model_size(model["meta"].get("n_params", 0))
        
    except Exception as e:
        # If all fails, mark as unknown but don't crash

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
    
    # Enhanced context window patterns with more accurate detection
    context_patterns = {
        r'qwen.*3.*235.*a22b': 131072,  # Qwen3-235B-A22B has 131K context
        r'qwen.*3.*32.*bf16': 32768,    # Qwen3-32B-BF16
        r'qwen.*3.*32': 32768,          # Qwen3-32B variants
        r'qwen.*3': 32768,              # Qwen3 default
        r'llama.*4': 32768,             # Llama 4 models
        r'deepseek.*coder.*33b': 16384, # DeepSeek Coder 33B
        r'deepseek': 32768,             # DeepSeek default
        r'codellama': 16384,            # Code Llama models
        r'phi.*3': 8192,                # Phi-3 models
        r'gemma.*2': 8192,              # Gemma 2 models
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
    
    # Match context window with more specific patterns first
    for pattern, ctx in context_patterns.items():
        if re.search(pattern, name_lower):
            n_ctx = ctx
            break
    
    return {
        "n_params": n_params,
        "n_ctx": n_ctx,
        "architecture": infer_architecture(name_lower),
        "quantization": infer_quantization(name_lower),
        "precision": infer_precision(name_lower),
        "context_window_formatted": format_context_window(n_ctx),
        "max_safe_tokens": calculate_max_safe_tokens(n_ctx)
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

def format_context_window(n_ctx: int) -> str:
    """Format context window size for display."""
    if n_ctx >= 100000:
        return f"{n_ctx // 1000}K tokens"
    elif n_ctx >= 1000:
        return f"{n_ctx // 1000}K tokens"
    else:
        return f"{n_ctx} tokens"

def calculate_max_safe_tokens(n_ctx: int) -> int:
    """Calculate safe maximum tokens for response (60% of context window for safety)."""
    return int(n_ctx * 0.6)
