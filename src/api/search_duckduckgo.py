from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

import asyncio


from utils.duckduckgo_search import DuckDuckGo

router = APIRouter()

    
class MultiSearchRequest(BaseModel):
    queries: list[str]
 
@router.post("/search/web/")
async def search_multi(request: MultiSearchRequest):
    try:
        duck = DuckDuckGo()
        tasks = [duck.search_duckduckgo(q) for q in request.queries]
        results = await asyncio.gather(*tasks)
        flat_list = [item for sublist in results for item in sublist]
        return flat_list
    except Exception as e:
        raise HTTPException(500, f"Parallel search failed: {e}")