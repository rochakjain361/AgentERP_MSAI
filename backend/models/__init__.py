"""Pydantic models for the application."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class ItemRequest(BaseModel):
    """Item request model for sales orders."""
    item_code: str
    qty: int


class AgentRequest(BaseModel):
    """Request model for agent orchestration."""
    intent: str
    customer: Optional[str] = None
    items: Optional[List[ItemRequest]] = None
    transaction_date: Optional[str] = None
    customer_data: Optional[Dict[str, Any]] = None
    company: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class AgentResponse(BaseModel):
    """Response model for agent operations."""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class Customer(BaseModel):
    """Customer model for ERPNext."""
    doctype: str = "Customer"
    customer_name: str
    customer_type: str = "Company"
    territory: str = "India"


class SalesOrderItem(BaseModel):
    """Sales order item model."""
    item_code: str
    qty: int


class SalesOrder(BaseModel):
    """Sales order model for ERPNext."""
    doctype: str = "Sales Order"
    customer: str
    transaction_date: str
    items: List[SalesOrderItem]


class ChatMessage(BaseModel):
    """Chat message model for persistence."""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str
    content: str
    type: str = "text"
    widget_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatSession(BaseModel):
    """Chat session model for persistence."""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
