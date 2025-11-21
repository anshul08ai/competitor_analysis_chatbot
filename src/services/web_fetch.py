
from typing import Any,List
from pydantic import BaseModel


from utils.duckduckgo_search import DuckDuckGo

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
    

