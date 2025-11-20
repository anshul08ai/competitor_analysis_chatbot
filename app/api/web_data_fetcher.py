from fastapi import APIRouter, Body, HTTPException
from typing import Any,List
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import sys

utils_path = Path.cwd().parent / "src" / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from duckduckgo_search import DuckDuckGo


router = APIRouter()
class SearchRequest(BaseModel):
    url: List[str]
    query: str

async def fetch_web_data(urls: List[str], query: str) -> Any:
    duck_obj = DuckDuckGo()
    try:
        results = await duck_obj.fetch_web_data(urls, query)
        return results
    except Exception as e:
        raise RuntimeError(f"Failed to fetch web data: {e}")

@router.post("/web/fetch", tags=["search"], summary="Fetch web data through API and summarize")
async def search_web(request: SearchRequest = Body(...)):
    try:
        search_results = await fetch_web_data(request.url, request.query)
        return search_results
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
