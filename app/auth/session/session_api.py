from fastapi import APIRouter, Depends
from auth.auth_routes import get_current_user
from auth.session.session_manager import SessionManager
from pydantic import BaseModel
 
router = APIRouter()

# ⭐ NEW ENDPOINT: List all user sessions
@router.get("/list")
def list_user_sessions(user: str = Depends(get_current_user)):
    print(f"s_a: {user}")
    return {"sessions": SessionManager.get_user_sessions(user)}

@router.post("/create-session")
def create_session(user: str = Depends(get_current_user)):
    return SessionManager.create_session(user_id=user)
 
@router.post("/guest-session")
def guest_session():
    return SessionManager.create_session(user_id=None)
 
@router.post("/{session_id}/message")
def add_message(session_id: str, role: str, message: str,bookmark: bool = False, url: list= None):
    return SessionManager.add_message(session_id, role, message)
 
@router.get("/{session_id}")
def get_session(session_id: str):
    return SessionManager.get_session(session_id)

@router.get("/{session_id}/history")
def get_history(session_id: str, user: str = Depends(get_current_user)):
    return {
        "session_id": session_id,
        "messages": SessionManager.get_chat_history(session_id)
    }

class UpdateBookmarkModel(BaseModel):
    msg_id: str
    bookmark: bool
 
@router.put("/{session_id}/update-bookmark")
def update_bookmark(
    session_id: str,
    data: UpdateBookmarkModel,
    user: str = Depends(get_current_user)
):
    return SessionManager.update_message_bookmark(
        session_id=session_id,
        msg_id=data.msg_id,
        bookmark=data.bookmark
    )
 
 