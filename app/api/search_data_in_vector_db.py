from fastapi import APIRouter, Body, HTTPException
from typing import Any
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import sys

# Add src/utils and src/prompt_engineering to sys.path for imports
utils_path = Path.cwd().parent / "src" / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from zilliz_vectorstore import search_in_vector_store

router = APIRouter()

@router.post("/search_in_vectorstore", tags=["search"],summary="Search in vector db",description="Search data in milvus vector database")
async def search_in_vectorstore( query: dict = Body(..., description="search data in vector store")):
    """
    Takes user input text and search it in the vector store.
    """
    try:
        status = await search_in_vector_store(query['query'])
        # if not status:
        #     raise HTTPException(status_code=200, detail="No relevant documents found in vector store.")
        return {'data':status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {e}")


