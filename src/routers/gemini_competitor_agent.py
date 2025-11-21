from fastapi import APIRouter, Body, HTTPException
from services.gemini_competitor import SearchRequest,perform_agent_graph_search


router = APIRouter()
@router.post("/gemini/competitor", tags=["LLM"], summary="Deep search agent")
async def search_web(request: SearchRequest = Body(...)):
    try:
        result = await perform_agent_graph_search(request.query)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
