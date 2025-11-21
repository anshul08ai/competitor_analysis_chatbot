from fastapi import APIRouter, Body, HTTPException
from services.web_fetch import SearchRequest, fetch_web_data


router = APIRouter()

@router.post("/web/fetch", tags=["search"], summary="Fetch web data through API and summarize")
async def search_web(request: SearchRequest = Body(...)):
    try:
        search_results = await fetch_web_data(request.url, request.query)
        return search_results
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
