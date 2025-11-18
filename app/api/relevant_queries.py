from fastapi import APIRouter, Body, HTTPException
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime
from pathlib import Path
import sys
# from src.prompt_engineering import generate_search_queries_prompt,generate_search_queries_system_prompt,generate_alternative_search_queries_system_prompt,generate_alternative_search_queries_prompt
# from src.llm.lite_llm_client import create_chat_model

utils_path = Path.cwd().parent / "src" / "llm"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

prompt_path = Path.cwd().parent / "src" / "prompt_engineering"
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from prompt_template import generate_search_queries_prompt,generate_search_queries_system_prompt,generate_alternative_search_queries_system_prompt,generate_alternative_search_queries_prompt
from lite_llm_client import create_chat_model

router = APIRouter()


class SearchQueryBody(BaseModel):
    query: str
    max_query_generation: int = 3
    previous_query_generated: Optional[List[str]] = None


@router.post("/search/relevant_queries", tags=["LLM Search"], summary="Generate relevant search queries",
             description="Generates relevant search queries based on user input using Huggingface LLM.")
async def generate_relevant_queries(payload: SearchQueryBody = Body(...)):
    try:
        user_query = payload.query
        max_gen = payload.max_query_generation
        previous_queries = payload.previous_query_generated

        current_date = datetime.today().strftime("%d %B %Y")
        connection_status = create_chat_model()

        if not connection_status.get('status'):
            raise HTTPException(status_code=503, detail="Unable to connect to LLM model")

        llm = connection_status['model']
        if not previous_queries:
            system_msg = SystemMessage(content=generate_search_queries_system_prompt)
            human_msg = HumanMessage(content=generate_search_queries_prompt.format(
                    user_query=user_query,
                    current_date=current_date,
                    MAX_QUERY_GENERATIONS=max_gen,
                ))
            response=llm.invoke([system_msg, human_msg])

            refined_queries = [
                q.strip().strip("'\"").strip("-").strip()
                for q in response.content.split("\n")
                if q and q.lower() != "none"
            ]
            refined_search_queries = refined_queries[:max_gen]
            return {"generated_queries": refined_search_queries}
        else:
            system_msg = SystemMessage(content=generate_alternative_search_queries_system_prompt)
            human_msg = HumanMessage(content=generate_alternative_search_queries_prompt.format(
                user_query=user_query,
                previous_queries="\n".join(previous_queries),
                MAX_QUERY_GENERATIONS=max_gen
            ))
            response = llm.invoke([system_msg, human_msg])
            refined_queries = [
                q.strip().strip("'\"").strip("-").strip()
                for q in response.content.split("\n")
                if q and q.lower() != "none"
            ]
            refined_search_queries = refined_queries[:max_gen]
            return {"generated_queries": refined_search_queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error to fetch relevant query: {e}")

   
