from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from pathlib import Path
import sys

utils_path = Path.cwd().parent / "src" / "graph"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from workflow import AgentGraph



router = APIRouter()
agent_graph = AgentGraph()
compiled = agent_graph.compile()

class SearchRequest(BaseModel):
    query: str

async def perform_agent_graph_search(query: str):
    try:
        output = compiled.invoke({'query': query})
        return output
    except Exception as e:
        raise RuntimeError(f"Agent graph invocation failed: {e}")

@router.post("/gemini/competitor", tags=["LLM"], summary="Deep search agent")
async def search_web(request: SearchRequest = Body(...)):
    try:
        result = await perform_agent_graph_search(request.query)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
