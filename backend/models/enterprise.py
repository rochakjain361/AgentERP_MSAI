"""Authentication and User Management Models."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    VIEWER = "viewer"       # Read-only access
    OPERATOR = "operator"   # Can create records
    MANAGER = "manager"     # Can approve/edit
    ADMIN = "admin"         # Full control


class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    role: UserRole = UserRole.OPERATOR  # Default role
    company: Optional[str] = None  # Associated company/customer in ERPNext


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data (excludes password)."""
    id: str
    email: str
    name: str
    role: UserRole
    company: Optional[str] = None  # Associated company/customer
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============== AUDIT MODELS ==============

class AuditAction(str, Enum):
    """Types of actions that can be audited."""
    # Auth actions
    USER_LOGIN = "user_login"
    USER_REGISTER = "user_register"
    
    # ERP actions
    CREATE_ORDER = "create_order"
    UPDATE_ORDER = "update_order"
    DELETE_ORDER = "delete_order"
    CREATE_CUSTOMER = "create_customer"
    UPDATE_CUSTOMER = "update_customer"
    QUERY_DATA = "query_data"
    
    # Approval actions
    REQUEST_APPROVAL = "request_approval"
    APPROVE_REQUEST = "approve_request"
    REJECT_REQUEST = "reject_request"
    
    # Tool actions
    CREATE_TOOL = "create_tool"
    RUN_TOOL = "run_tool"
    DELETE_TOOL = "delete_tool"
    
    # AI actions
    AI_SUGGESTION = "ai_suggestion"
    AI_CHAT = "ai_chat"


class AuditLogCreate(BaseModel):
    """Model for creating audit log entries."""
    user_id: str
    user_email: str
    user_role: UserRole
    action: AuditAction
    resource_type: str  # e.g., "Sales Order", "Customer"
    resource_id: Optional[str] = None
    input_params: Optional[dict] = None
    result: Literal["success", "failure", "pending"]
    result_message: Optional[str] = None
    ai_reasoning: Optional[str] = None  # Why action was taken/suggested
    approval_required: bool = False
    approval_id: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Response model for audit log entries."""
    id: str
    user_id: str
    user_email: str
    user_role: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    input_params: Optional[dict]
    result: str
    result_message: Optional[str]
    ai_reasoning: Optional[str]
    approval_required: bool
    approval_id: Optional[str]
    timestamp: datetime


# ============== APPROVAL MODELS ==============

class ApprovalStatus(str, Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRule(str, Enum):
    """Rules that trigger approval requirements."""
    HIGH_VALUE_ORDER = "high_value_order"  # Order > ₹50,000
    NEW_CUSTOMER_LARGE_ORDER = "new_customer_large_order"
    BULK_DELETE = "bulk_delete"
    MANUAL_REQUEST = "manual_request"


class ApprovalRequestCreate(BaseModel):
    """Model for creating approval requests."""
    requester_id: str
    requester_email: str
    requester_role: UserRole
    action_type: AuditAction
    resource_type: str
    resource_data: dict  # The data to be actioned
    rule_triggered: ApprovalRule
    reason: str  # Why approval is needed
    ai_analysis: Optional[str] = None  # AI's assessment


class ApprovalRequestResponse(BaseModel):
    """Response model for approval requests."""
    id: str
    requester_id: str
    requester_email: str
    requester_role: str
    action_type: str
    resource_type: str
    resource_data: dict
    rule_triggered: str
    reason: str
    ai_analysis: Optional[str]
    status: ApprovalStatus
    reviewer_id: Optional[str] = None
    reviewer_email: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None


class ApprovalDecision(BaseModel):
    """Model for approval/rejection decision."""
    decision: Literal["approve", "reject"]
    notes: Optional[str] = None


# ============== PROACTIVE INSIGHTS MODELS ==============

class InsightPriority(str, Enum):
    """Priority levels for insights."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InsightType(str, Enum):
    """Types of proactive insights."""
    PENDING_APPROVAL = "pending_approval"
    HIGH_VALUE_ORDERS = "high_value_orders"
    DELAYED_ORDERS = "delayed_orders"
    LOW_INVENTORY = "low_inventory"
    OVERDUE_INVOICES = "overdue_invoices"
    NEW_OPPORTUNITIES = "new_opportunities"


class ProactiveInsight(BaseModel):
    """Model for a proactive insight/suggestion."""
    id: str
    type: InsightType
    priority: InsightPriority
    title: str  # Short headline
    context: str  # What's happening
    reason: str  # Why this matters
    action_label: str  # CTA button text
    action_type: str  # What action to take
    action_params: Optional[dict] = None  # Parameters for the action
    affected_count: int  # Number of items affected
    potential_value: Optional[float] = None  # ₹ value if applicable
    generated_at: datetime


class InsightsResponse(BaseModel):
    """Response model for proactive insights."""
    insights: List[ProactiveInsight]
    generated_at: datetime
    user_role: str


# ============== BUSINESS IMPACT MODELS ==============

class BusinessImpactMetrics(BaseModel):
    """Model for business impact calculations."""
    total_actions_today: int
    total_actions_month: int
    manual_time_per_action_mins: float = 10.0
    agent_time_per_action_mins: float = 2.5
    time_saved_today_mins: float
    time_saved_month_hours: float
    efficiency_gain_percent: float
    estimated_monthly_actions: int = 500
    projected_monthly_savings_hours: float
    cost_per_hour: float = 500.0  # ₹500/hour assumption
    projected_monthly_savings_inr: float
