"""Approval Service - Workflow for approval-required actions."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

from database import db
from models.enterprise import (
    ApprovalStatus, ApprovalRule, AuditAction, UserRole
)
from services.audit_service import audit_service

logger = logging.getLogger(__name__)

# Approval thresholds
HIGH_VALUE_ORDER_THRESHOLD = 50000  # ₹50,000


class ApprovalService:
    """Service for managing approval workflows."""

    def _serialize_dt(self, value: Any) -> Any:
        """Return ISO datetime string when value is datetime, otherwise passthrough."""
        return value.isoformat() if hasattr(value, "isoformat") else value

    def _get_mock_pending_approvals(self) -> List[Dict[str, Any]]:
        """Temporary fallback data for demo when pending queue is empty."""
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "mock-approval-001",
                "requester_id": "mock-operator-001",
                "requester_email": "operator@agenterp.com",
                "requester_role": UserRole.OPERATOR.value,
                "action_type": "create_order",
                "resource_type": "SalesOrder",
                "resource_data": {
                    "name": "SAL-ORD-MOCK-001",
                    "customer": "TechCorp Solutions",
                    "grand_total": 182500,
                    "items": [
                        {"item_code": "ERP-LIC-PRO", "qty": 5, "rate": 25000},
                        {"item_code": "IMPLEMENT-SVC", "qty": 1, "rate": 57500}
                    ]
                },
                "rule_triggered": ApprovalRule.HIGH_VALUE_ORDER.value,
                "reason": "Order value exceeds approval threshold and requires manager review",
                "ai_analysis": "High-value order from repeat customer. Margins look healthy; recommend approval after confirming payment terms.",
                "status": ApprovalStatus.PENDING.value,
                "reviewer_id": None,
                "reviewer_email": None,
                "review_notes": None,
                "created_at": (now).isoformat(),
                "reviewed_at": None,
                "is_mock": True
            },
            {
                "id": "mock-approval-002",
                "requester_id": "mock-operator-002",
                "requester_email": "operator@agenterp.com",
                "requester_role": UserRole.OPERATOR.value,
                "action_type": "update_order",
                "resource_type": "SalesOrder",
                "resource_data": {
                    "name": "SAL-ORD-MOCK-002",
                    "customer": "Global Industries Ltd",
                    "grand_total": 94000,
                    "items": [
                        {"item_code": "ANALYTICS-ADDON", "qty": 2, "rate": 47000}
                    ]
                },
                "rule_triggered": ApprovalRule.HIGH_VALUE_ORDER.value,
                "reason": "Updated order total now crosses threshold and needs approval",
                "ai_analysis": "Customer payment pattern is stable. Low operational risk, moderate exposure.",
                "status": ApprovalStatus.PENDING.value,
                "reviewer_id": None,
                "reviewer_email": None,
                "review_notes": None,
                "created_at": (now).isoformat(),
                "reviewed_at": None,
                "is_mock": True
            }
        ]
    
    @property
    def approvals_collection(self):
        return db["approval_requests"]
    
    def check_approval_required(
        self,
        action_type: AuditAction,
        user_role: str,
        resource_data: dict
    ) -> Optional[Dict[str, Any]]:
        """Check if an action requires approval based on rules."""
        
        # Admins bypass approval
        if user_role == UserRole.ADMIN.value:
            return None
        
        # Viewers can't create anything
        if user_role == UserRole.VIEWER.value:
            return {
                "required": True,
                "rule": "no_permission",
                "reason": "Viewers do not have permission for this action"
            }
        
        # Check high-value order rule
        if action_type in [AuditAction.CREATE_ORDER, AuditAction.UPDATE_ORDER]:
            grand_total = resource_data.get("grand_total", 0)
            if grand_total > HIGH_VALUE_ORDER_THRESHOLD:
                return {
                    "required": True,
                    "rule": ApprovalRule.HIGH_VALUE_ORDER.value,
                    "reason": f"Order value ₹{grand_total:,.2f} exceeds threshold of ₹{HIGH_VALUE_ORDER_THRESHOLD:,}",
                    "threshold": HIGH_VALUE_ORDER_THRESHOLD
                }
        
        # Check new customer + large order
        if action_type == AuditAction.CREATE_ORDER:
            is_new_customer = resource_data.get("is_new_customer", False)
            grand_total = resource_data.get("grand_total", 0)
            if is_new_customer and grand_total > 25000:
                return {
                    "required": True,
                    "rule": ApprovalRule.NEW_CUSTOMER_LARGE_ORDER.value,
                    "reason": f"New customer with order value ₹{grand_total:,.2f} requires verification"
                }
        
        # Operators can't delete
        if user_role == UserRole.OPERATOR.value and action_type in [
            AuditAction.DELETE_ORDER,
            AuditAction.BULK_DELETE if hasattr(AuditAction, 'BULK_DELETE') else None
        ]:
            return {
                "required": True,
                "rule": "role_restriction",
                "reason": "Operators cannot delete records without manager approval"
            }
        
        return None
    
    async def create_approval_request(
        self,
        requester_id: str,
        requester_email: str,
        requester_role: str,
        action_type: AuditAction,
        resource_type: str,
        resource_data: dict,
        rule_triggered: str,
        reason: str,
        ai_analysis: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new approval request."""
        try:
            approval_id = str(uuid.uuid4())
            
            approval_doc = {
                "id": approval_id,
                "requester_id": requester_id,
                "requester_email": requester_email,
                "requester_role": requester_role,
                "action_type": action_type.value if isinstance(action_type, AuditAction) else action_type,
                "resource_type": resource_type,
                "resource_data": resource_data,
                "rule_triggered": rule_triggered,
                "reason": reason,
                "ai_analysis": ai_analysis,
                "status": ApprovalStatus.PENDING.value,
                "reviewer_id": None,
                "reviewer_email": None,
                "review_notes": None,
                "created_at": datetime.now(timezone.utc),
                "reviewed_at": None
            }
            
            await self.approvals_collection.insert_one(approval_doc)
            
            # Log to audit
            await audit_service.log_action(
                user_id=requester_id,
                user_email=requester_email,
                user_role=requester_role,
                action=AuditAction.REQUEST_APPROVAL,
                resource_type=resource_type,
                input_params={"rule": rule_triggered, "value": resource_data.get("grand_total")},
                result="pending",
                result_message=reason,
                ai_reasoning=ai_analysis,
                approval_required=True,
                approval_id=approval_id
            )
            
            logger.info(f"Approval request created: {approval_id} by {requester_email}")
            
            return {
                "status": "approval_required",
                "approval_id": approval_id,
                "rule": rule_triggered,
                "reason": reason,
                "message": f"This action requires manager approval: {reason}"
            }
            
        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_pending_approvals(
        self,
        reviewer_role: str = None
    ) -> Dict[str, Any]:
        """Get all pending approval requests."""
        try:
            # Only managers and admins can see pending approvals
            if reviewer_role and reviewer_role not in [UserRole.MANAGER.value, UserRole.ADMIN.value]:
                return {"status": "error", "message": "Insufficient permissions"}
            
            cursor = self.approvals_collection.find(
                {"status": ApprovalStatus.PENDING.value},
                {"_id": 0}
            ).sort("created_at", -1)
            
            approvals = []
            async for doc in cursor:
                doc["created_at"] = self._serialize_dt(doc.get("created_at"))
                if doc.get("reviewed_at"):
                    doc["reviewed_at"] = self._serialize_dt(doc.get("reviewed_at"))
                approvals.append(doc)

            # Temporary demo fallback: keep at least 2 pending items visible.
            if len(approvals) < 2:
                existing_ids = {a.get("id") for a in approvals}
                for mock in self._get_mock_pending_approvals():
                    if mock.get("id") not in existing_ids:
                        approvals.append(mock)
                    if len(approvals) >= 2:
                        break
            
            return {
                "status": "success",
                "approvals": approvals,
                "count": len(approvals)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def process_approval(
        self,
        approval_id: str,
        reviewer_id: str,
        reviewer_email: str,
        reviewer_role: str,
        decision: str,  # "approve" or "reject"
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process an approval request (approve/reject)."""
        try:
            # Verify reviewer has permission
            if reviewer_role not in [UserRole.MANAGER.value, UserRole.ADMIN.value]:
                return {"status": "error", "message": "Only managers and admins can approve requests"}
            
            # Find the approval request
            approval = await self.approvals_collection.find_one({"id": approval_id})
            if not approval:
                return {"status": "error", "message": "Approval request not found"}
            
            if approval["status"] != ApprovalStatus.PENDING.value:
                return {"status": "error", "message": f"Request already {approval['status']}"}
            
            # Update approval
            new_status = ApprovalStatus.APPROVED.value if decision == "approve" else ApprovalStatus.REJECTED.value
            
            await self.approvals_collection.update_one(
                {"id": approval_id},
                {"$set": {
                    "status": new_status,
                    "reviewer_id": reviewer_id,
                    "reviewer_email": reviewer_email,
                    "review_notes": notes,
                    "reviewed_at": datetime.now(timezone.utc)
                }}
            )
            
            # Log to audit
            await audit_service.log_action(
                user_id=reviewer_id,
                user_email=reviewer_email,
                user_role=reviewer_role,
                action=AuditAction.APPROVE_REQUEST if decision == "approve" else AuditAction.REJECT_REQUEST,
                resource_type="ApprovalRequest",
                resource_id=approval_id,
                input_params={"decision": decision, "notes": notes},
                result="success",
                result_message=f"Request {new_status} by {reviewer_email}",
                approval_id=approval_id
            )
            
            logger.info(f"Approval {approval_id} {new_status} by {reviewer_email}")
            
            # If approved, return the original data so action can proceed
            result = {
                "status": "success",
                "decision": decision,
                "approval_status": new_status,
                "message": f"Request {new_status}"
            }
            
            if decision == "approve":
                result["proceed_with_action"] = True
                result["action_type"] = approval["action_type"]
                result["resource_type"] = approval["resource_type"]
                result["resource_data"] = approval["resource_data"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing approval: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_approval_by_id(self, approval_id: str) -> Dict[str, Any]:
        """Get a specific approval request."""
        try:
            approval = await self.approvals_collection.find_one(
                {"id": approval_id},
                {"_id": 0}
            )
            
            if not approval:
                return {"status": "error", "message": "Approval not found"}
            
            approval["created_at"] = self._serialize_dt(approval.get("created_at"))
            if approval.get("reviewed_at"):
                approval["reviewed_at"] = self._serialize_dt(approval.get("reviewed_at"))
            
            return {"status": "success", "approval": approval}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_user_approvals(self, user_id: str) -> Dict[str, Any]:
        """Get approval requests made by a user."""
        try:
            cursor = self.approvals_collection.find(
                {"requester_id": user_id},
                {"_id": 0}
            ).sort("created_at", -1)
            
            approvals = []
            async for doc in cursor:
                doc["created_at"] = self._serialize_dt(doc.get("created_at"))
                if doc.get("reviewed_at"):
                    doc["reviewed_at"] = self._serialize_dt(doc.get("reviewed_at"))
                approvals.append(doc)
            
            return {"status": "success", "approvals": approvals, "count": len(approvals)}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
approval_service = ApprovalService()
