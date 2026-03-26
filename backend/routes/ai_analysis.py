"""
AI Risk Analysis Routes - API endpoints for AI Intelligence Analysis.

Role-Based Access:
- Admin and Manager: Full access to AI analysis and actions
- Employee and Other roles: No access (403 Forbidden)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from services.ai_risk_analysis import ai_risk_analysis
from routes.auth import require_auth

router = APIRouter(prefix="/ai-analysis", tags=["ai-analysis"])
logger = logging.getLogger(__name__)

# Roles that can access AI Analysis
AI_AUTHORIZED_ROLES = ["admin", "manager"]


def require_ai_access(user: dict = Depends(require_auth)):
    """Dependency to check if user can access AI Analysis."""
    if user.get("role") not in AI_AUTHORIZED_ROLES:
        raise HTTPException(
            status_code=403,
            detail="AI Intelligence Analysis is only available for Admin and Manager roles"
        )
    return user


class ExecuteActionRequest(BaseModel):
    """Request to execute an AI-suggested action."""
    action_id: str
    customer: str
    order_analysis_id: str


@router.get("/analyze")
async def analyze_orders(user: dict = Depends(require_ai_access)):
    """
    Analyze all orders and classify risk.
    
    Only accessible by Admin and Manager.
    
    Returns:
    - Risk classification for each customer/order
    - Reasoning for each classification
    - Suggested actions based on risk level
    - Auto-actions that were triggered (for critical risks)
    """
    try:
        user_company = user.get("company")
        
        result = await ai_risk_analysis.analyze_orders(
            company_filter=user_company if user.get("role") != "admin" else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_action(
    request: ExecuteActionRequest,
    user: dict = Depends(require_ai_access)
):
    """
    Execute an AI-suggested action.
    
    Only accessible by Admin and Manager.
    Actions are logged to audit trail.
    """
    try:
        result = await ai_risk_analysis.execute_action(
            action_id=request.action_id,
            customer=request.customer,
            order_analysis_id=request.order_analysis_id,
            user_id=user["id"],
            user_email=user["email"],
            user_role=user["role"],
            company=user.get("company")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Action execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/access-check")
async def check_ai_access(user: dict = Depends(require_auth)):
    """
    Check if current user has access to AI Analysis.
    Returns access status without throwing error.
    """
    has_access = user.get("role") in AI_AUTHORIZED_ROLES
    
    return {
        "has_access": has_access,
        "role": user.get("role"),
        "message": "AI Analysis available" if has_access else "AI Analysis requires Admin or Manager role"
    }
