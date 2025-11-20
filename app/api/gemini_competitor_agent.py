from fastapi import APIRouter, Body, HTTPException
from typing import Any,List
from pydantic import BaseModel
from datetime import datetime
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

@router.post("/gemini/competitor", tags=["LLM"], summary="Deep search agent")
async def search_web(request: SearchRequest = Body(...)):
    try:
        ouptut =compiled.invoke({'query':request.query})
        return  ouptut
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")
