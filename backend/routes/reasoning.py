"""
Reasoning Routes - API endpoints for proactive analysis and workflow execution.

Implements:
- Today's priorities endpoint
- Situation details endpoint  
- Execute action sequence endpoint
- Workflow status endpoint
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging

from services.reasoning_engine import reasoning_engine
from services.sequence_executor import sequence_executor
from routes.auth import require_auth, get_current_user

router = APIRouter(prefix="/reasoning", tags=["reasoning"])
logger = logging.getLogger(__name__)


class ExecuteSequenceRequest(BaseModel):
    """Request to execute a sequence of actions."""
    situation_id: str
    situation_type: str
    selected_actions: List[str]
    context_data: dict


@router.get("/priorities")
async def get_todays_priorities(user: dict = Depends(require_auth)):
    """
    Get today's priorities - proactive analysis of ERP state.
    
    Returns situations requiring attention:
    - Payment delays
    - High-value orders
    - Other risk situations
    
    Each situation includes:
    - Reasoning summary
    - Metrics checked
    - Severity classification
    - Suggested actions
    - Expected impact
    """
    try:
        user_role = user.get("role", "viewer")
        user_company = user.get("company")
        
        result = await reasoning_engine.get_todays_priorities(
            user_role=user_role,
            company_filter=user_company if user_role != "admin" else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting priorities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-delays")
async def analyze_payment_delays(user: dict = Depends(require_auth)):
    """
    Analyze payment delays - the hero scenario.
    
    Returns detailed analysis of customers with overdue payments:
    - Severity classification (critical/high/medium/low)
    - Metrics: overdue days, outstanding amount, payment history
    - Suggested actions based on severity
    - Expected business impact
    """
    try:
        user_role = user.get("role", "viewer")
        user_company = user.get("company")
        
        situations = await reasoning_engine.analyze_payment_delays(
            company_filter=user_company if user_role != "admin" else None
        )
        
        return {
            "status": "success",
            "count": len(situations),
            "situations": situations
        }
        
    except Exception as e:
        logger.error(f"Error analyzing payment delays: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_action_sequence(
    request: ExecuteSequenceRequest,
    user: dict = Depends(require_auth)
):
    """
    Execute a sequence of actions based on user selection.
    
    Workflow:
    1. Parse selected actions
    2. Check approval requirements
    3. Execute each step in order
    4. Verify each step succeeded
    5. Calculate business impact
    6. Return step-by-step results
    
    Request body:
    - situation_id: ID of the analyzed situation
    - situation_type: Type (payment_delay, high_value_order, etc.)
    - selected_actions: List of action IDs to execute
    - context_data: Data needed for execution
    
    Returns:
    - workflow_id: Track the execution
    - workflow_status: completed/partial/failed/awaiting_approval
    - steps: Step-by-step results with verification
    - business_impact: Quantified impact
    """
    try:
        # Check if user can execute actions
        if user.get("role") == "viewer":
            raise HTTPException(
                status_code=403,
                detail="Viewers cannot execute actions. Contact a manager or admin."
            )
        
        result = await sequence_executor.execute_sequence(
            situation_id=request.situation_id,
            situation_type=request.situation_type,
            selected_actions=request.selected_actions,
            context_data=request.context_data,
            user_id=user["id"],
            user_email=user["email"],
            user_role=user["role"],
            company=user.get("company")
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing sequence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    user: dict = Depends(require_auth)
):
    """
    Get the current status of a workflow execution.
    
    Returns:
    - Workflow details
    - Step-by-step status
    - Business impact (if completed)
    """
    try:
        result = await sequence_executor.get_workflow_status(workflow_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/situation/{situation_id}")
async def get_situation_details(
    situation_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific situation.
    
    (Placeholder - in production would fetch from DB)
    """
    return {
        "status": "success",
        "message": "Situation details would be fetched from cache/DB",
        "situation_id": situation_id
    }
