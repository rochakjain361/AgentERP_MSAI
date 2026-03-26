"""
Manager Intelligence Routes - AI-powered dashboard for managers.

Provides comprehensive business intelligence using Azure AI Foundry Agent.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import logging

from services.agent_intelligence import agent_intelligence
from routes.auth import require_auth

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
logger = logging.getLogger(__name__)


class AnalyzeSituationRequest(BaseModel):
    """Request to analyze a specific situation."""
    situation_type: str
    context_data: dict


@router.get("/dashboard")
async def get_manager_intelligence(user: dict = Depends(require_auth)):
    """
    Get comprehensive AI-powered manager intelligence dashboard.
    
    This endpoint:
    1. Gathers real ERP data (orders, invoices, customers)
    2. Sends data to Azure AI Foundry Agent for analysis
    3. Returns structured insights including:
       - Executive summary
       - Key findings with severity
       - Risks and mitigations
       - Opportunities
       - Prioritized recommendations
       - Health score
    
    Only available for managers and admins.
    """
    try:
        # Check if user is manager or admin
        if user.get("role") not in ["manager", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Manager Intelligence Dashboard is only available for managers and admins"
            )
        
        user_company = user.get("company")
        
        # Get AI-powered intelligence
        result = await agent_intelligence.get_manager_intelligence(
            company_filter=user_company if user.get("role") != "admin" else None
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligence dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_situation(
    request: AnalyzeSituationRequest,
    user: dict = Depends(require_auth)
):
    """
    Use AI to analyze a specific business situation.
    
    Provides deep AI analysis for situations like:
    - Payment delays
    - High-value orders
    - Customer churn risk
    - Revenue opportunities
    """
    try:
        if user.get("role") == "viewer":
            raise HTTPException(
                status_code=403,
                detail="Situation analysis requires manager or operator access"
            )
        
        user_company = user.get("company")
        
        result = await agent_intelligence.analyze_specific_situation(
            situation_type=request.situation_type,
            context_data=request.context_data,
            company_filter=user_company if user.get("role") != "admin" else None
        )
        
        return {
            "status": "success",
            "analysis": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Situation analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check")
async def check_ai_health(user: dict = Depends(require_auth)):
    """Check if AI services are available."""
    try:
        # Quick test of AI service
        from services.agent_intelligence import AZURE_AGENT_ENDPOINT, AZURE_OPENAI_ENDPOINT
        
        return {
            "status": "success",
            "agent_configured": bool(AZURE_AGENT_ENDPOINT),
            "openai_configured": bool(AZURE_OPENAI_ENDPOINT),
            "using_agent": agent_intelligence.use_agent
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
