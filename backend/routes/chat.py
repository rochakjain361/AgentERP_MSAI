"""Chat routes - Handles chat sessions and messages."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import logging

from database import db, is_mongodb_available
from models import ChatMessage, ChatSession

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions")
async def create_chat_session():
    """Create a new chat session."""
    if not is_mongodb_available():
        # Return a mock session for development
        session = ChatSession()
        doc = session.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        return {"status": "success", "session": doc}

    try:
        session = ChatSession()
        doc = session.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.chat_sessions.insert_one(doc)
        doc.pop('_id', None)
        return {"status": "success", "session": doc}
    except Exception as e:
        logging.error(f"Failed to create chat session: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/sessions")
async def get_chat_sessions():
    """Get all chat sessions."""
    if not is_mongodb_available():
        # Return empty list for development
        return []

    try:
        sessions = await db.chat_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(100)
        return sessions
    except Exception as e:
        logging.error(f"Failed to get chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get a specific chat session."""
    if not is_mongodb_available():
        raise HTTPException(status_code=404, detail="Session not found (database unavailable)")

    try:
        session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logging.error(f"Failed to get chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/sessions/{session_id}")
async def update_chat_session(session_id: str, title: str = None):
    """Update chat session title."""
    if not is_mongodb_available():
        return {"status": "success"}  # Mock success for development

    try:
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if title:
            update_data["title"] = title
        
        result = await db.chat_sessions.update_one(
            {"id": session_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Failed to update chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and its messages."""
    if not is_mongodb_available():
        return {"status": "success"}  # Mock success for development

    try:
        result = await db.chat_sessions.delete_one({"id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await db.chat_messages.delete_many({"session_id": session_id})
        
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Failed to delete chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/messages")
async def save_chat_message(message: ChatMessage):
    """Save chat message to database."""
    if not is_mongodb_available():
        return {"status": "success"}  # Mock success for development

    try:
        doc = message.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(doc)
        
        await db.chat_sessions.update_one(
            {"id": message.session_id},
            {
                "$inc": {"message_count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        session = await db.chat_sessions.find_one({"id": message.session_id})
        if session and session.get("message_count", 0) == 1 and message.role == "user":
            title = message.content[:50] + ("..." if len(message.content) > 50 else "")
            await db.chat_sessions.update_one(
                {"id": message.session_id},
                {"$set": {"title": title}}
            )
        
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Failed to save chat message: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/messages/{session_id}")
async def get_chat_messages(session_id: str):
    """Get chat history for a session."""
    if not is_mongodb_available():
        return []  # Return empty messages for development

    try:
        messages = await db.chat_messages.find({"session_id": session_id}, {"_id": 0}).sort("timestamp", 1).to_list(1000)
        return messages
    except Exception as e:
        logging.error(f"Failed to get chat messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")
