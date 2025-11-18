import uuid
import json
from redis_client import redis_client
from datetime import datetime
 
class SessionManager:
 
    @staticmethod
    def create_session(user_id: str = None):
        session_id = f"SESSION_{uuid.uuid4().hex}"
        print(f"session_id : {session_id}")
        session_key = f"session:{session_id}"
 
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "messages": []
        }
        print(f"session_data : {session_data}")
        # Store session
        redis_client.set(session_key, json.dumps(session_data))
 
        # Store session under user_sessions set
        if user_id:
            redis_client.sadd(f"user_sessions:{user_id}", session_id)
 
        return {"session_id": session_id}
    
    @staticmethod
    def add_message(session_id: str, role: str, message: str, bookmark: bool = False, url: str = None):
        session_key = f"session:{session_id}"
        print(f"session_key : {session_key}")
        raw = redis_client.get(session_key)
        print(f"add_msg_key_present :")
        if not raw:
            print(f"add_msg_key_present : Not present")
            return {"error": "Session not found"}
        print(f"add_msg_key_present : Present")
        session_data = json.loads(raw)
        print(f"add_msg_session_data : {session_data}")
 
        msg_id = f"msg_{len(session_data['messages'])+1}"
 
        new_msg = {
            "id": msg_id,
            "role": role,
            "message": message,
            "bookmark": bookmark,
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"new_msg : {new_msg}")
        session_data["messages"].append(new_msg)
 
        redis_client.set(session_key, json.dumps(session_data))
 
        return {"status": "message_added", "message": new_msg}
    
    # @staticmethod
    # def add_message(session_id: str, role: str, message: str, bookmarks: bool = False, url: str = None):
    
    #     session_key = f"session:{session_id}"
    #     data = redis_client.get(session_key)
    
    #     if not data:
    #         return {"error": "Session not found"}
    
    #     session_data = json.loads(data)
    
    #     msg_id = f"msg_{len(session_data['messages']) + 1}"
    
    #     session_data["messages"].append({
    #         "id": msg_id,
    #         "role": role,
    #         "message": message,
    #         "bookmark": bookmarks,
    #         "url": url,
    #         "timestamp": datetime.utcnow().isoformat()
    #     })
    
    #     redis_client.set(session_key, json.dumps(session_data))
    #     return {"status": "message_added", "message_id": msg_id}
    
    @staticmethod
    def get_session(session_id: str):
        session_key = f"session:{session_id}"
        session_data = redis_client.get(session_key)
 
        if not session_data:
            return {"error": "Session not found"}
 
        return json.loads(session_data)
 
    @staticmethod
    def get_user_sessions(user_id: str):
        """Return all sessions for a logged-in user"""
        redis_key = f"user_sessions:{user_id}"   # << FIXED HERE
        sessions = redis_client.smembers(redis_key)
        if not sessions:
            return []
 
        # decode bytes → str
        return [s.encode() for s in sessions]
    
    @staticmethod
    def get_chat_history(session_id: str):
        session_key = f"session:{session_id}"
        print(f"session_key : {session_key}")
        data = redis_client.get(session_key)
        if not data:
            return None
        
        session_data = json.loads(data)
        print(f"get_chat_h_session_data : {session_data}")
        return session_data.get("messages", [])
    
    @staticmethod
    def update_message_bookmark(session_id: str, msg_id: str, bookmark: bool):
    
        session_key = f"session:{session_id}"
        data = redis_client.get(session_key)
    
        if not data:
            return {"error": "Session not found"}
    
        session_data = json.loads(data)
        messages = session_data["messages"]
    
        updated = False
    
        for msg in messages:
            if msg["id"] == msg_id:
                msg["bookmark"] = bookmark
                msg["bookmark_updated_at"] = datetime.utcnow().isoformat()
                updated = True
                break
    
        if not updated:
            return {"error": "Message ID not found"}
    
        redis_client.set(session_key, json.dumps(session_data))
    
        return {
            "status": "bookmark_updated",
            "message_id": msg_id,
            "bookmark": bookmark
        }
 