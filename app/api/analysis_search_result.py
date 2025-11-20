from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from fastapi import APIRouter, Body, HTTPException
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from typing import List,Optional, Any
from datetime import datetime
from pathlib import Path
import requests
import sys
import yaml

url_path = Path(__file__).parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with url_path.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
summarize_output_url =url_config['summarize_output_url']


utils_path = Path.cwd().parent / "src" / "llm"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

prompt_path = Path.cwd().parent / "src" / "prompt_engineering"
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from prompt_template import analysis_result_content_prompt
from lite_llm_client import create_chat_model
from prompt_template import final_news_report_prompt,final_news_report_system_prompt

router = APIRouter()


class CompetitorInfo(BaseModel):
   name: str = Field("", description="The name of the competitor.")
   description: str = Field("", description="A short evidence-based description of the competitor.")
   website: str = Field("", description="Official website URL of the competitor if available.")
   products: List[str] = Field(default_factory=list, description="List of competitor's products mentioned in evidence.")
   strengths: List[str] = Field(default_factory=list, description="Strengths of this competitor based on evidence.")
   weaknesses: List[str] = Field(default_factory=list, description="Weaknesses or limitations mentioned in the documents.")
   pricing_notes: List[str] = Field(default_factory=list, description="Pricing insights or notes based on evidence.")
   feature_highlights: List[str] = Field(default_factory=list, description="Feature highlights identified for this competitor.")
   market_position: str = Field("", description="Market positioning label if explicitly mentioned (e.g., Leader, Challenger).")

class ProductInfo(BaseModel):
   name: str = Field("", description="Name of the product.")
   description: str = Field("", description="Short description of the product based on evidence.")
   key_features: List[str] = Field(default_factory=list, description="Key features of the product.")
   pricing: str = Field("", description="Pricing details if mentioned.")
   url: str = Field("", description="Reference URL for the product if available.")
   target_segment: str = Field("", description="Mentioned target customer segment (Enterprise, SMB, Developers, etc.).")

class AnalysisModel(BaseModel):
   competitors: List[CompetitorInfo] = Field(
       default_factory=list,
       description="Detailed competitor-level insights extracted strictly from evidence."
   )
   products: List[ProductInfo] = Field(
       default_factory=list,
       description="Detailed product-level insights extracted from evidence."
   )
   pricing: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="Grouped pricing insights for each competitor or product."
   )
   features: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="Grouped feature insights for each competitor or product."
   )
   strengths: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="General strengths grouped per entity, strictly based on evidence."
   )
   weaknesses: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="General weaknesses grouped per entity based on evidence."
   )
   opportunities: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="Opportunities mentioned in the research documents."
   )
   threats: Dict[str, List[str]] = Field(
       default_factory=dict,
       description="Threats mentioned in the research documents."
   )
   market_moves: List[str] = Field(
       default_factory=list,
       description="Any important market moves or strategic actions taken, based strictly on evidence."
   )
   risks: List[str] = Field(
       default_factory=list,
       description="Risks identified from the verified research documents."
   )
   differentiators: List[str] = Field(
       default_factory=list,
       description="Unique differentiators found in the research."
   )
   summary: str = Field(
       "",
       description="A concise 500 sentence summary directly answering the main query."
   )
   best_url: Optional[str] = Field(
       None,
       description="The 5 most best relevant source URL supporting the summary."
   )
   class Config:
       extra = "forbid"


class AnlysisContentBody(BaseModel):
    query: str
    url_with_summary: Any 
    with_summarize: bool = False

async def perform_analysis(user_query: str, url_with_summary: Any, with_summarize: bool):
    analysis_prompt = analysis_result_content_prompt.format(
        main_query=user_query,
        documents_with_urls=str(url_with_summary)
    )
    connection_status = create_chat_model()

    if not connection_status.get('status'):
        raise RuntimeError("Unable to connect to LLM model")

    llm = connection_status['model']
    structured_output = llm.invoke(analysis_prompt)

    if with_summarize:
        try:
            system_msg = SystemMessage(content=final_news_report_system_prompt)
            human_msg = HumanMessage(content=final_news_report_prompt.format(
                user_query=user_query,
                search_results=str(structured_output)
            ))
            summarized_content = llm.invoke([system_msg, human_msg])
            structured_output.summary = summarized_content.content
        except Exception:
            pass

    return structured_output

@router.post("/analysis/", tags=["Analysis"], summary="Analysis data with query")
async def analysis_content(payload: AnlysisContentBody = Body(...)):
    try:
        result = await perform_analysis(payload.query, payload.url_with_summary, payload.with_summarize)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {e}")
