"""Approval routes - Workflow management for approval-required actions."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from models.enterprise import ApprovalDecision
from routes.auth import require_auth, require_manager
from services.approval_service import approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_pending_approvals(user: dict = Depends(require_manager)):
    """
    Get all pending approval requests.
    Only managers and admins can view pending approvals.
    """
    return await approval_service.get_pending_approvals(reviewer_role=user["role"])


@router.get("/my-requests")
async def get_my_approval_requests(user: dict = Depends(require_auth)):
    """Get approval requests created by the current user."""
    return await approval_service.get_user_approvals(user["id"])


@router.get("/{approval_id}")
async def get_approval_detail(
    approval_id: str,
    user: dict = Depends(require_auth)
):
    """Get details of a specific approval request."""
    result = await approval_service.get_approval_by_id(approval_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Check if user has permission to view
    approval = result["approval"]
    if user["role"] not in ["manager", "admin"] and approval["requester_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return result


@router.post("/{approval_id}/decide")
async def process_approval_decision(
    approval_id: str,
    decision: ApprovalDecision,
    user: dict = Depends(require_manager)
):
    """
    Approve or reject an approval request.
    Only managers and admins can process approvals.
    """
    result = await approval_service.process_approval(
        approval_id=approval_id,
        reviewer_id=user["id"],
        reviewer_email=user["email"],
        reviewer_role=user["role"],
        decision=decision.decision,
        notes=decision.notes
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{approval_id}/approve")
async def approve_request(
    approval_id: str,
    notes: Optional[str] = None,
    user: dict = Depends(require_manager)
):
    """Quick approve an approval request."""
    return await approval_service.process_approval(
        approval_id=approval_id,
        reviewer_id=user["id"],
        reviewer_email=user["email"],
        reviewer_role=user["role"],
        decision="approve",
        notes=notes
    )


@router.post("/{approval_id}/reject")
async def reject_request(
    approval_id: str,
    notes: Optional[str] = None,
    user: dict = Depends(require_manager)
):
    """Quick reject an approval request."""
    return await approval_service.process_approval(
        approval_id=approval_id,
        reviewer_id=user["id"],
        reviewer_email=user["email"],
        reviewer_role=user["role"],
        decision="reject",
        notes=notes
    )
