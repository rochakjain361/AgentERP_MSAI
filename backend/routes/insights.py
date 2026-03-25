"""Insights routes - Proactive suggestions and business impact metrics."""
from fastapi import APIRouter, Depends
import logging

from routes.auth import require_auth, get_current_user
from services.proactive_engine import proactive_engine

router = APIRouter(prefix="/insights", tags=["insights"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_proactive_insights(user: dict = Depends(require_auth)):
    """
    Get proactive insights filtered by user's company.
    Admin sees all, others see only their company's data.
    """
    user_company = user.get("company") if user["role"] != "admin" else None
    return await proactive_engine.generate_insights(user["role"], user_company)


@router.get("/suggestions")
async def get_chat_suggestions(user: dict = Depends(require_auth)):
    """
    Get contextual chat suggestions based on ERP state.
    These appear as actionable prompts in the chat.
    """
    user_company = user.get("company") if user["role"] != "admin" else None
    suggestions = await proactive_engine.generate_chat_suggestions(user["role"], user_company)
    return {
        "status": "success",
        "suggestions": suggestions,
        "user_role": user["role"],
        "company": user_company
    }


@router.get("/public")
async def get_public_insights(user: dict = Depends(get_current_user)):
    """
    Get insights without strict auth (for dashboard preview).
    """
    role = user["role"] if user else "viewer"
    company = user.get("company") if user and user["role"] != "admin" else None
    return await proactive_engine.generate_insights(role, company)


@router.get("/impact")
async def get_business_impact(user: dict = Depends(require_auth)):
    """Get business impact metrics showing time/cost savings."""
    return await proactive_engine.get_business_impact_metrics()
