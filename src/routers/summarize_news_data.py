from fastapi import APIRouter, Body, HTTPException
from services.final_report import SummarizationNewsRequest,perform_summarization


router = APIRouter()
@router.post("/final-report", tags=["summarization"], summary="Summarize text news content")
async def news_summarize(request: SummarizationNewsRequest = Body(...)) -> dict:
    try:
        summary = await perform_summarization(request.query, request.search_results)
        return {"summary": summary}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")
