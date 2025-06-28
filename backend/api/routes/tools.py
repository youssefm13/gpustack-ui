from fastapi import APIRouter, HTTPException, Request
from services.tavily_search import perform_web_search_async
from api.schemas import SearchRequest, SearchResponse, ErrorResponse

router = APIRouter()

@router.post("/search", response_model=SearchResponse, responses={500: {"model": ErrorResponse}})
async def web_search(request: SearchRequest, req: Request) -> SearchResponse:
    """
    Perform AI-enhanced web search with smart summaries.
    
    This endpoint sends a search query to the AI-backed Tavily search engine and
    retrieves a comprehensive response containing summarized search results with sources.
    
    - **query**: The search phrase or terms to use in the web search
    
    Returns:
        SearchResponse: AI-processed search results
        
    Raises:
        HTTPException: If there is an error during the search process
    """
    try:
        # Use shared HTTP client from app state
        http_client = getattr(req.app.state, 'http_client', None)
        result = await perform_web_search_async(request.q, http_client)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

