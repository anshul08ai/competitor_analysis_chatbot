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

from zilliz_vectorstore import store_in_vector_store

router = APIRouter()

@router.post("/store_in_vectorstore", tags=["Store"],summary="Store in vector db",description="Store important data in milvus vector database")
async def store_documents_in_vectorstore( input: dict = Body(..., description="Input text to store in vector store")):
    """
    Takes user input text and stores it in the vector store.
    """
    try:
        status = await store_in_vector_store(input['input'])
        if not status:
            raise HTTPException(status_code=500, detail="Failed to store documents in vector store.")
        return {"status": "Documents stored successfully in vector store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing documents: {e}")


