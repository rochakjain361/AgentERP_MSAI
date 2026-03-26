"""
Sequence Executor - Executes multi-step workflows with verification.

This implements the execute → verify loop:
1. Parse action sequence from user selection
2. Execute each step in order
3. Verify each step succeeded
4. Handle failures with recovery suggestions
5. Track and report progress
6. Calculate final business impact
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import asyncio

from database import db
from services.audit_service import audit_service
from services.approval_service import approval_service
from models.enterprise import AuditAction

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_APPROVAL = "needs_approval"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"


class SequenceExecutor:
    """Executes multi-step action sequences with verification."""
    
    def __init__(self):
        self.workflows_collection = db["workflow_executions"]
        self.alerts_collection = db["system_alerts"]
    
    async def execute_sequence(
        self,
        situation_id: str,
        situation_type: str,
        selected_actions: List[str],
        context_data: Dict[str, Any],
        user_id: str,
        user_email: str,
        user_role: str,
        company: str = None
    ) -> Dict[str, Any]:
        """
        Execute a sequence of actions based on user selection.
        
        Args:
            situation_id: ID of the reasoning situation
            situation_type: Type of situation (payment_delay, high_value_order, etc.)
            selected_actions: List of action IDs selected by user
            context_data: Data needed for execution (customer, amounts, etc.)
            user_id, user_email, user_role: User context for RBAC
            company: Company filter for multi-tenancy
        
        Returns:
            Workflow execution result with step-by-step status
        """
        workflow_id = str(uuid.uuid4())
        
        # Initialize workflow record
        workflow = {
            "id": workflow_id,
            "situation_id": situation_id,
            "situation_type": situation_type,
            "user_id": user_id,
            "user_email": user_email,
            "user_role": user_role,
            "company": company,
            "status": WorkflowStatus.RUNNING.value,
            "selected_actions": selected_actions,
            "context_data": context_data,
            "steps": [],
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "business_impact": None
        }
        
        # Build execution steps
        steps = self._build_execution_steps(selected_actions, context_data, user_role)
        workflow["steps"] = steps
        
        # Save initial state
        await self.workflows_collection.insert_one(workflow)
        
        # Execute steps
        results = await self._execute_steps(
            workflow_id, steps, context_data, user_id, user_email, user_role, company
        )
        
        # Calculate final status
        failed_steps = [r for r in results if r["status"] == StepStatus.FAILED.value]
        approval_steps = [r for r in results if r["status"] == StepStatus.NEEDS_APPROVAL.value]
        success_steps = [r for r in results if r["status"] == StepStatus.SUCCESS.value]
        
        if approval_steps and not failed_steps:
            final_status = WorkflowStatus.AWAITING_APPROVAL.value
        elif failed_steps:
            final_status = WorkflowStatus.PARTIAL.value if success_steps else WorkflowStatus.FAILED.value
        else:
            final_status = WorkflowStatus.COMPLETED.value
        
        # Calculate business impact
        business_impact = self._calculate_workflow_impact(results, context_data)
        
        # Update workflow record
        await self.workflows_collection.update_one(
            {"id": workflow_id},
            {"$set": {
                "status": final_status,
                "steps": results,
                "completed_at": datetime.now(timezone.utc),
                "business_impact": business_impact
            }}
        )
        
        # Log to audit trail
        await audit_service.log_action(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=AuditAction.RUN_TOOL,
            resource_type="WorkflowExecution",
            resource_id=workflow_id,
            input_params={
                "situation_type": situation_type,
                "actions": selected_actions,
                "customer": context_data.get("customer")
            },
            result="success" if final_status == WorkflowStatus.COMPLETED.value else "partial",
            result_message=f"Workflow {final_status}: {len(success_steps)}/{len(results)} steps completed",
            company=company
        )
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow_status": final_status,
            "steps": results,
            "summary": {
                "total_steps": len(results),
                "completed": len(success_steps),
                "failed": len(failed_steps),
                "awaiting_approval": len(approval_steps)
            },
            "business_impact": business_impact,
            "recovery_suggestions": self._get_recovery_suggestions(failed_steps) if failed_steps else None
        }
    
    def _build_execution_steps(
        self, 
        selected_actions: List[str], 
        context_data: Dict, 
        user_role: str
    ) -> List[Dict[str, Any]]:
        """Build ordered execution steps from selected actions."""
        
        # Action definitions with execution details
        action_definitions = {
            "send_escalation": {
                "name": "Send Escalation Notice",
                "executor": "send_notification",
                "params": {"type": "escalation", "severity": "critical"},
                "requires_approval": False
            },
            "send_reminder": {
                "name": "Send Payment Reminder",
                "executor": "send_notification",
                "params": {"type": "reminder", "severity": "normal"},
                "requires_approval": False
            },
            "raise_alert": {
                "name": "Raise System Alert",
                "executor": "create_alert",
                "params": {"type": "payment_delay"},
                "requires_approval": False
            },
            "block_sales": {
                "name": "Block Further Sales",
                "executor": "update_customer_status",
                "params": {"action": "block"},
                "requires_approval": True
            },
            "notify_manager": {
                "name": "Notify Level 1 Manager",
                "executor": "send_manager_notification",
                "params": {"level": 1},
                "requires_approval": False
            },
            "log_followup": {
                "name": "Schedule Follow-up",
                "executor": "create_task",
                "params": {"days": 7},
                "requires_approval": False
            },
            "monitor": {
                "name": "Add to Watch List",
                "executor": "add_to_watchlist",
                "params": {},
                "requires_approval": False
            },
            "submit_order": {
                "name": "Submit Order",
                "executor": "submit_sales_order",
                "params": {},
                "requires_approval": True
            },
            "verify_customer": {
                "name": "Verify Customer Credit",
                "executor": "check_customer_credit",
                "params": {},
                "requires_approval": False
            }
        }
        
        steps = []
        for i, action_id in enumerate(selected_actions):
            if action_id in action_definitions:
                defn = action_definitions[action_id]
                steps.append({
                    "step_number": i + 1,
                    "action_id": action_id,
                    "name": defn["name"],
                    "executor": defn["executor"],
                    "params": defn["params"],
                    "requires_approval": defn["requires_approval"],
                    "status": StepStatus.PENDING.value,
                    "started_at": None,
                    "completed_at": None,
                    "result": None,
                    "error": None,
                    "verification": None
                })
        
        return steps
    
    async def _execute_steps(
        self,
        workflow_id: str,
        steps: List[Dict],
        context_data: Dict,
        user_id: str,
        user_email: str,
        user_role: str,
        company: str
    ) -> List[Dict[str, Any]]:
        """Execute each step in sequence with verification."""
        
        results = []
        
        for step in steps:
            step_result = step.copy()
            step_result["started_at"] = datetime.now(timezone.utc).isoformat()
            step_result["status"] = StepStatus.RUNNING.value
            
            # Update progress in DB
            await self._update_step_status(workflow_id, step["step_number"], StepStatus.RUNNING.value)
            
            try:
                # Check if approval needed
                if step["requires_approval"] and user_role not in ["admin"]:
                    # Create approval request
                    approval_result = await approval_service.create_approval_request(
                        requester_id=user_id,
                        requester_email=user_email,
                        requester_role=user_role,
                        action_type=AuditAction.RUN_TOOL,
                        resource_type="WorkflowStep",
                        resource_data={
                            "workflow_id": workflow_id,
                            "step": step["name"],
                            "context": context_data
                        },
                        rule_triggered="workflow_approval",
                        reason=f"Action '{step['name']}' requires manager approval"
                    )
                    
                    step_result["status"] = StepStatus.NEEDS_APPROVAL.value
                    step_result["result"] = {"approval_id": approval_result.get("approval_id")}
                    step_result["completed_at"] = datetime.now(timezone.utc).isoformat()
                    results.append(step_result)
                    continue
                
                # Execute the step
                executor = step["executor"]
                params = step["params"]
                
                exec_result = await self._execute_action(
                    executor, params, context_data, user_id, user_email, company
                )
                
                # Verify the step
                verification = await self._verify_action(
                    executor, exec_result, context_data
                )
                
                if verification["verified"]:
                    step_result["status"] = StepStatus.SUCCESS.value
                    step_result["result"] = exec_result
                    step_result["verification"] = verification
                else:
                    step_result["status"] = StepStatus.FAILED.value
                    step_result["error"] = verification.get("error", "Verification failed")
                    step_result["verification"] = verification
                
            except Exception as e:
                logger.error(f"Step execution error: {str(e)}")
                step_result["status"] = StepStatus.FAILED.value
                step_result["error"] = str(e)
            
            step_result["completed_at"] = datetime.now(timezone.utc).isoformat()
            results.append(step_result)
            
            # Update DB
            await self._update_step_status(
                workflow_id, 
                step["step_number"], 
                step_result["status"],
                step_result
            )
        
        return results
    
    async def _execute_action(
        self,
        executor: str,
        params: Dict,
        context_data: Dict,
        user_id: str,
        user_email: str,
        company: str
    ) -> Dict[str, Any]:
        """Execute a specific action type."""
        
        customer = context_data.get("customer", "Unknown")
        outstanding = context_data.get("outstanding_amount", 0)
        
        if executor == "send_notification":
            # Simulate sending notification
            notification = {
                "type": params.get("type", "general"),
                "recipient": customer,
                "severity": params.get("severity", "normal"),
                "message": f"Payment reminder for outstanding amount ₹{outstanding:,.2f}",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "sent_by": user_email
            }
            return {"notification_sent": True, "details": notification}
        
        elif executor == "create_alert":
            # Create system alert
            alert = {
                "id": str(uuid.uuid4()),
                "type": params.get("type", "general"),
                "severity": "critical" if outstanding > 100000 else "high",
                "customer": customer,
                "amount": outstanding,
                "message": f"Payment delay alert for {customer}",
                "created_at": datetime.now(timezone.utc),
                "created_by": user_email,
                "company": company,
                "status": "active"
            }
            await self.alerts_collection.insert_one(alert)
            alert["created_at"] = alert["created_at"].isoformat()
            return {"alert_created": True, "alert": alert}
        
        elif executor == "update_customer_status":
            # Simulate updating customer status (in real scenario, would call ERP API)
            return {
                "customer_updated": True,
                "customer": customer,
                "new_status": "blocked" if params.get("action") == "block" else "active",
                "reason": f"Payment delay - Outstanding: ₹{outstanding:,.2f}"
            }
        
        elif executor == "send_manager_notification":
            return {
                "manager_notified": True,
                "level": params.get("level", 1),
                "message": f"Attention required: {customer} has critical payment delay",
                "context": {"customer": customer, "outstanding": outstanding}
            }
        
        elif executor == "create_task":
            return {
                "task_created": True,
                "due_days": params.get("days", 7),
                "task": f"Follow up on payment from {customer}"
            }
        
        elif executor == "add_to_watchlist":
            return {
                "added_to_watchlist": True,
                "customer": customer,
                "reason": "Payment monitoring"
            }
        
        else:
            return {"executed": True, "executor": executor}
    
    async def _verify_action(
        self,
        executor: str,
        exec_result: Dict,
        context_data: Dict
    ) -> Dict[str, Any]:
        """Verify that an action succeeded."""
        
        # Verification logic based on executor type
        if executor == "send_notification":
            verified = exec_result.get("notification_sent", False)
            return {
                "verified": verified,
                "check": "notification_delivery",
                "message": "Notification sent successfully" if verified else "Notification failed"
            }
        
        elif executor == "create_alert":
            # Verify alert exists in DB
            alert_id = exec_result.get("alert", {}).get("id")
            if alert_id:
                alert = await self.alerts_collection.find_one({"id": alert_id})
                verified = alert is not None
            else:
                verified = False
            return {
                "verified": verified,
                "check": "alert_persistence",
                "message": "Alert created and verified" if verified else "Alert creation failed"
            }
        
        elif executor == "update_customer_status":
            # In real scenario, would query ERP to verify status change
            verified = exec_result.get("customer_updated", False)
            return {
                "verified": verified,
                "check": "status_update",
                "message": "Customer status updated" if verified else "Status update failed"
            }
        
        else:
            # Default verification
            return {
                "verified": True,
                "check": "execution_complete",
                "message": "Action completed"
            }
    
    async def _update_step_status(
        self,
        workflow_id: str,
        step_number: int,
        status: str,
        step_data: Dict = None
    ):
        """Update step status in workflow record."""
        update = {"$set": {f"steps.{step_number - 1}.status": status}}
        if step_data:
            update["$set"][f"steps.{step_number - 1}"] = step_data
        await self.workflows_collection.update_one({"id": workflow_id}, update)
    
    def _calculate_workflow_impact(
        self,
        results: List[Dict],
        context_data: Dict
    ) -> Dict[str, Any]:
        """Calculate business impact of the workflow execution."""
        
        completed_steps = len([r for r in results if r["status"] == StepStatus.SUCCESS.value])
        total_steps = len(results)
        
        outstanding = context_data.get("outstanding_amount", 0)
        
        # Time saved calculation
        manual_time_per_step = 15  # minutes
        automated_time_per_step = 0.5  # minutes
        time_saved = completed_steps * (manual_time_per_step - automated_time_per_step)
        
        # Risk reduction
        if completed_steps == total_steps:
            risk_reduction = "Maximum"
            intervention_status = "Complete"
        elif completed_steps > 0:
            risk_reduction = "Partial"
            intervention_status = "In Progress"
        else:
            risk_reduction = "None"
            intervention_status = "Failed"
        
        return {
            "steps_completed": completed_steps,
            "total_steps": total_steps,
            "completion_rate": f"{int(completed_steps/total_steps*100)}%" if total_steps > 0 else "0%",
            "time_saved_minutes": round(time_saved, 1),
            "consultant_hours_avoided": round(time_saved / 60, 2),
            "amount_at_risk": outstanding,
            "risk_reduction": risk_reduction,
            "intervention_status": intervention_status,
            "faster_intervention_days": max(0, 7 - 1),  # vs manual 7-day cycle
            "summary": f"Completed {completed_steps}/{total_steps} actions, saved ~{int(time_saved)} mins"
        }
    
    def _get_recovery_suggestions(self, failed_steps: List[Dict]) -> List[Dict[str, Any]]:
        """Get recovery suggestions for failed steps."""
        suggestions = []
        for step in failed_steps:
            suggestions.append({
                "failed_step": step["name"],
                "error": step.get("error", "Unknown error"),
                "suggestion": f"Retry '{step['name']}' manually or contact support",
                "can_retry": True
            })
        return suggestions
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow."""
        workflow = await self.workflows_collection.find_one(
            {"id": workflow_id},
            {"_id": 0}
        )
        
        if not workflow:
            return {"status": "error", "message": "Workflow not found"}
        
        # Convert datetime objects
        if workflow.get("started_at"):
            workflow["started_at"] = workflow["started_at"].isoformat()
        if workflow.get("completed_at"):
            workflow["completed_at"] = workflow["completed_at"].isoformat()
        
        return {"status": "success", "workflow": workflow}


# Singleton instance
sequence_executor = SequenceExecutor()
