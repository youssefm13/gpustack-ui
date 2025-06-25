from fastapi import APIRouter, HTTPException
from services.tavily_search import perform_web_search

router = APIRouter()

@router.post("/search")
async def web_search(query: dict):
    try:
        result = perform_web_search(query.get("q", ""))
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

