"""Audit routes - Activity log and audit trail."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
import logging

from routes.auth import require_auth, require_manager
from services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user: dict = Depends(require_auth)
):
    """
    Get audit logs with optional filtering.
    All authenticated users can view audit logs.
    """
    # Non-admin/manager can only see their own logs
    if user["role"] not in ["manager", "admin"]:
        user_id = user["id"]
    
    return await audit_service.get_logs(
        limit=limit,
        offset=offset,
        user_id=user_id,
        action=action,
        resource_type=resource_type
    )


@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    user: dict = Depends(require_auth)
):
    """Get recent activity for dashboard."""
    # Non-admin/manager can only see their own activity
    if user["role"] not in ["manager", "admin"]:
        return await audit_service.get_logs(limit=limit, user_id=user["id"])
    return await audit_service.get_recent_activity(limit=limit)


@router.get("/summary/{user_id}")
async def get_user_activity_summary(
    user_id: str,
    current_user: dict = Depends(require_auth)
):
    """Get activity summary for a specific user."""
    # Users can only see their own summary unless manager/admin
    if current_user["role"] not in ["manager", "admin"] and current_user["id"] != user_id:
        return {"status": "error", "message": "Access denied"}
    
    return await audit_service.get_user_activity_summary(user_id)


@router.get("/stats")
async def get_audit_stats(user: dict = Depends(require_auth)):
    """Get audit statistics for business impact."""
    return await audit_service.get_action_count()
