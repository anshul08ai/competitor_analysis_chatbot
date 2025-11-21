
from fastapi import APIRouter, Body, HTTPException
from services.search_relevent_query import SearchQueryBody,generate_queries_logic
import sys


router = APIRouter()
@router.post("/search/relevant_queries", tags=["LLM Search"], summary="Generate relevant search queries",
             description="Generates relevant search queries based on user input using Huggingface LLM.")
async def generate_relevant_queries(payload: SearchQueryBody = Body(...)):
    try:
        generated_queries = await generate_queries_logic(payload.query, payload.max_query_generation, payload.previous_query_generated)
        return {"generated_queries": generated_queries}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error to fetch relevant query: {e}")
