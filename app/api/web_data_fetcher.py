from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import sys

# Add src/utils and src/prompt_engineering to sys.path for imports
utils_path = Path.cwd().parent / "src" / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from duckduckgo_search import DuckDuckGo

router = APIRouter()

class SearchRequest(BaseModel):
    url: str
    query: str

@router.post("/web/fetch", tags=["search"], summary="Fetch web data through api and summarize")
async def search_web(request: SearchRequest = Body(...)):
    try:
        output={}
        search_results  = []
        duck_obj = DuckDuckGo()
        search_results=duck_obj.fetch_web_data(request.url,request.query )
        output['url']=request.url
        output['summary']=search_results
        return output 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")