from fastapi import APIRouter, HTTPException, Request
from services.tavily_search import perform_web_search_async

router = APIRouter()

@router.post("/search")
async def web_search(query: dict, request: Request):
    try:
        # Use shared HTTP client from app state
        http_client = getattr(request.app.state, 'http_client', None)
        result = await perform_web_search_async(query.get("q", ""), http_client)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

