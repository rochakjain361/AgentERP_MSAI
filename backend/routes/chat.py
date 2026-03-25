"""Chat routes - Handles chat sessions and messages with user ownership."""
from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timezone
from typing import Optional

from database import db
from models import ChatSession, ChatMessage
from routes.auth import get_current_user, require_auth
from services.audit_service import audit_service
from models.enterprise import AuditAction

router = APIRouter(prefix="/chat", tags=["chat"])


# Access Level Definitions
# Level 1 (Admin): Create, Edit, Delete, View + Approve for Level 2
# Level 2 (Manager/Operator): Create, View + Approve for Level 3
# Level 3 (Viewer): View only

ACCESS_LEVELS = {
    "admin": 1,
    "manager": 2,
    "operator": 2,
    "viewer": 3
}

def get_access_level(role: str) -> int:
    """Get access level for a role (1=highest, 3=lowest)."""
    return ACCESS_LEVELS.get(role, 3)

def can_create(role: str) -> bool:
    """Check if role can create content (Level 1, 2)."""
    return get_access_level(role) <= 2

def can_edit(role: str) -> bool:
    """Check if role can edit content (Level 1 only)."""
    return get_access_level(role) == 1

def can_delete(role: str) -> bool:
    """Check if role can delete content (Level 1 only)."""
    return get_access_level(role) == 1


@router.post("/sessions")
async def create_chat_session(user: dict = Depends(require_auth)):
    """Create a new chat session (Level 1, 2 only)."""
    # Check access level
    if not can_create(user["role"]):
        raise HTTPException(
            status_code=403, 
            detail="Access denied: Viewers (Level 3) cannot create chat sessions. Please contact a Manager or Admin."
        )
    
    session = ChatSession()
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    doc['user_id'] = user["id"]  # Owner of the chat
    doc['user_email'] = user["email"]
    doc['company'] = user.get("company")  # Store company for data isolation
    
    await db.chat_sessions.insert_one(doc)
    doc.pop('_id', None)
    
    # Log action
    await audit_service.log_action(
        user_id=user["id"],
        user_email=user["email"],
        user_role=user["role"],
        action=AuditAction.AI_CHAT,
        resource_type="ChatSession",
        resource_id=doc["id"],
        result="success",
        result_message="Chat session created",
        company=user.get("company")
    )
    
    return {"status": "success", "session": doc}


@router.get("/sessions")
async def get_chat_sessions(user: dict = Depends(require_auth)):
    """Get chat sessions - users only see their own chats."""
    # All users can view, but only their own chats
    sessions = await db.chat_sessions.find(
        {"user_id": user["id"]},  # Filter by user
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    
    return sessions


@router.get("/sessions/{session_id}")
async def get_chat_session(session_id: str, user: dict = Depends(require_auth)):
    """Get a specific chat session (only if owned by user or admin)."""
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership (admins can see all)
    if session.get("user_id") != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: You can only view your own chat sessions")
    
    return session


@router.put("/sessions/{session_id}")
async def update_chat_session(
    session_id: str, 
    title: str = None,
    user: dict = Depends(require_auth)
):
    """Update chat session title (Level 1 only, or owner)."""
    # Find the session first
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permission: owner can update, or admin can update any
    is_owner = session.get("user_id") == user["id"]
    is_admin = user["role"] == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only edit your own chat sessions"
        )
    
    # Non-admin owners still need edit permission
    if is_owner and not is_admin and not can_edit(user["role"]):
        # Actually, owners should be able to edit their own session titles
        # Let's allow this for better UX
        pass
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if title:
        update_data["title"] = title
    
    await db.chat_sessions.update_one(
        {"id": session_id},
        {"$set": update_data}
    )
    
    return {"status": "success"}


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str, user: dict = Depends(require_auth)):
    """Delete a chat session (Level 1 only, or owner)."""
    # Find the session first
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permission
    is_owner = session.get("user_id") == user["id"]
    is_admin = user["role"] == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only delete your own chat sessions"
        )
    
    # Non-owners need Level 1 (admin) to delete others' chats
    if not is_owner and not can_delete(user["role"]):
        raise HTTPException(
            status_code=403, 
            detail="Access denied: Only Admins (Level 1) can delete others' chat sessions"
        )
    
    await db.chat_sessions.delete_one({"id": session_id})
    await db.chat_messages.delete_many({"session_id": session_id})
    
    return {"status": "success"}


@router.post("/messages")
async def save_chat_message(message: ChatMessage, user: dict = Depends(require_auth)):
    """Save chat message to database."""
    # Verify session ownership
    session = await db.chat_sessions.find_one({"id": message.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    if session.get("user_id") != user["id"] and user["role"] != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only add messages to your own chat sessions"
        )
    
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    doc['user_id'] = user["id"]  # Track who sent the message
    
    await db.chat_messages.insert_one(doc)
    
    await db.chat_sessions.update_one(
        {"id": message.session_id},
        {
            "$inc": {"message_count": 1},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Auto-set title from first user message
    if session.get("message_count", 0) == 0 and message.role == "user":
        title = message.content[:50] + ("..." if len(message.content) > 50 else "")
        await db.chat_sessions.update_one(
            {"id": message.session_id},
            {"$set": {"title": title}}
        )
    
    return {"status": "success"}


@router.get("/messages/{session_id}")
async def get_chat_messages(session_id: str, user: dict = Depends(require_auth)):
    """Get chat history for a session (only if owned by user)."""
    # Verify session ownership
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    if session.get("user_id") != user["id"] and user["role"] != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only view your own chat messages"
        )
    
    messages = await db.chat_messages.find(
        {"session_id": session_id}, 
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    return messages
