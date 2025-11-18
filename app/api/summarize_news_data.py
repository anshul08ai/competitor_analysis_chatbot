from fastapi import APIRouter, Body, HTTPException
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from typing import Any
import sys


# Add src/utils and src/prompt_engineering to sys.path for imports
utils_path = Path.cwd().parent / "src" / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

prompt_path = Path.cwd().parent / "src" / "prompt_engineering"
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from prompt_template import final_news_report_prompt,final_news_report_system_prompt
from lite_llm_client import create_chat_model

router = APIRouter()

class SummarizationNewsRequest(BaseModel):
    query: str
    search_results:Any

@router.post("/final-report", tags=["summarization"], summary="Summarize text news content")
async def news_summarize(request: SummarizationNewsRequest = Body(...)) -> dict:
    try:
        """
        Summarizes news content based on user query and search results.
        """
        connection_status = create_chat_model()

        if not connection_status.get('status'):
            raise HTTPException(status_code=503, detail="Unable to connect to LLM model")

        llm = connection_status['model']

        system_msg = SystemMessage(content=final_news_report_system_prompt)
        human_msg = HumanMessage(content=final_news_report_prompt.format(user_query=request.query, search_results=request.search_results))
        summarized_content=llm.invoke([system_msg, human_msg])
        return {"summary": summarized_content.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")
