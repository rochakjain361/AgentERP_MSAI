"""
AI Risk Analysis Service - Evaluates order risk and suggests interventions.

Risk Classification:
- CRITICAL: amount_due > 50000 AND days_overdue > 30 → Red
- MEDIUM: (amount_due < 50000 AND days_overdue > 30) OR (amount_due > 50000 AND days_overdue < 30) → Yellow  
- LOW: amount_due < 50000 AND days_overdue < 30 → Green
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from enum import Enum
import logging

from database import db
from services.erp_entity_service import erp_entity_service
from services.audit_service import audit_service
from models.enterprise import AuditAction

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    MEDIUM = "medium"
    LOW = "low"


# Thresholds
AMOUNT_THRESHOLD = 50000  # ₹50,000
DAYS_THRESHOLD = 30  # 30 days


class AIRiskAnalysisService:
    """Service for AI-powered order risk analysis."""
    
    def __init__(self):
        self.alerts_collection = db["ai_alerts"]
        self.actions_collection = db["ai_actions"]
    
    def classify_risk(self, amount_due: float, days_overdue: int) -> RiskLevel:
        """
        Classify risk based on amount and overdue days.
        
        CRITICAL: amount_due > 50000 AND days_overdue > 30
        MEDIUM: (amount_due < 50000 AND days_overdue > 30) OR (amount_due > 50000 AND days_overdue < 30)
        LOW: amount_due < 50000 AND days_overdue < 30
        """
        if amount_due >= AMOUNT_THRESHOLD and days_overdue >= DAYS_THRESHOLD:
            return RiskLevel.CRITICAL
        elif (amount_due < AMOUNT_THRESHOLD and days_overdue >= DAYS_THRESHOLD) or \
             (amount_due >= AMOUNT_THRESHOLD and days_overdue < DAYS_THRESHOLD):
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _to_number(self, value: Any) -> float:
        """Safely convert values from ERP payloads into float."""
        try:
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            return float(str(value).replace(",", "").strip())
        except Exception:
            return 0.0

    def _parse_date(self, value: Any):
        """Parse date from ERP string/date/datetime payloads."""
        if not value:
            return None
        try:
            if isinstance(value, str):
                return datetime.strptime(value[:10], "%Y-%m-%d").date()
            if hasattr(value, "date"):
                return value.date()
            return value
        except Exception:
            return None
    
    def get_reasoning(self, risk_level: RiskLevel, amount_due: float, days_overdue: int) -> str:
        """Generate human-readable reasoning for the risk classification."""
        if risk_level == RiskLevel.CRITICAL:
            return f"Open exposure is high (₹{amount_due:,.0f}) and aging is severe ({days_overdue} days), signaling immediate cash-flow and collection risk."
        elif risk_level == RiskLevel.MEDIUM:
            if amount_due >= AMOUNT_THRESHOLD:
                return f"Material exposure detected (₹{amount_due:,.0f}) with manageable aging ({days_overdue} days). Prioritize structured follow-up."
            else:
                return f"Aging is elevated ({days_overdue} days) with moderate exposure (₹{amount_due:,.0f}). Escalated reminder cadence is recommended."
        else:
            return f"Exposure (₹{amount_due:,.0f}) and aging ({days_overdue} days) remain within control bands. Continue standard monitoring."
    
    def get_suggested_actions(self, risk_level: RiskLevel, customer: str) -> List[Dict[str, Any]]:
        """Get suggested actions based on risk level."""
        if risk_level == RiskLevel.CRITICAL:
            return [
                {
                    "id": "stop_sales",
                    "label": "Stop Future Sales",
                    "description": f"Block all new sales orders for {customer}",
                    "action_type": "restriction",
                    "requires_confirmation": True,
                    "is_automatic": False,
                    "severity": "high"
                },
                {
                    "id": "escalate_management",
                    "label": "Escalate to Senior Management",
                    "description": "Notify senior management and sales team about critical risk",
                    "action_type": "escalation",
                    "requires_confirmation": True,
                    "is_automatic": False,
                    "severity": "high"
                },
                {
                    "id": "send_critical_reminder",
                    "label": "Send Critical Payment Reminder",
                    "description": "Immediately send critical payment reminder to customer",
                    "action_type": "notification",
                    "requires_confirmation": False,
                    "is_automatic": True,  # Auto-triggered for critical
                    "severity": "critical"
                }
            ]
        elif risk_level == RiskLevel.MEDIUM:
            return [
                {
                    "id": "send_reminder",
                    "label": "Send Payment Reminder",
                    "description": f"Send payment reminder to {customer}",
                    "action_type": "notification",
                    "requires_confirmation": True,
                    "is_automatic": False,
                    "severity": "medium"
                },
                {
                    "id": "escalate_tracking",
                    "label": "Escalate for Traceability",
                    "description": "Create tracking ticket for follow-up",
                    "action_type": "escalation",
                    "requires_confirmation": True,
                    "is_automatic": False,
                    "severity": "medium"
                }
            ]
        else:
            # LOW risk - standard operational options only
            return [
                {
                    "id": "view_order",
                    "label": "View Order Details",
                    "description": "View complete order information",
                    "action_type": "view",
                    "requires_confirmation": False,
                    "is_automatic": False,
                    "severity": "low"
                },
                {
                    "id": "continue_workflow",
                    "label": "Continue Workflow",
                    "description": "Proceed with standard order processing",
                    "action_type": "workflow",
                    "requires_confirmation": False,
                    "is_automatic": False,
                    "severity": "low"
                }
            ]
    
    async def analyze_orders(self, company_filter: str = None) -> Dict[str, Any]:
        """
        Analyze all orders and classify risk.
        Returns structured analysis with reasoning and actions.
        """
        try:
            # Fetch all invoices (for outstanding amounts)
            invoices_result = await erp_entity_service.query(
                doctype="Sales Invoice",
                filters=[],
                fields=["name", "customer", "grand_total", "outstanding_amount", 
                        "status", "due_date", "posting_date"],
                limit=100,
                company_filter=company_filter
            )
            
            # Fetch all orders
            orders_result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[],
                fields=["name", "customer", "grand_total", "status", 
                        "transaction_date", "delivery_date"],
                limit=100,
                company_filter=company_filter
            )
            
            analyzed_orders = []
            auto_actions_triggered = []
            today = datetime.now(timezone.utc).date()
            
            # Build customer outstanding map from invoices
            customer_outstanding = {}
            for invoice in invoices_result.get("data", []):
                customer = invoice.get("customer", "Unknown")
                outstanding = self._to_number(invoice.get("outstanding_amount", 0))
                due_date_str = invoice.get("due_date")
                
                if customer not in customer_outstanding:
                    customer_outstanding[customer] = {
                        "total_outstanding": 0,
                        "max_overdue_days": 0,
                        "invoices": []
                    }
                
                customer_outstanding[customer]["total_outstanding"] += outstanding
                customer_outstanding[customer]["invoices"].append(invoice)
                
                # Calculate overdue days
                if due_date_str and outstanding > 0:
                    try:
                        due_date = self._parse_date(due_date_str)
                        overdue_days = max(0, (today - due_date).days) if due_date else 0
                        if overdue_days > customer_outstanding[customer]["max_overdue_days"]:
                            customer_outstanding[customer]["max_overdue_days"] = overdue_days
                    except Exception:
                        pass
            
            # Add draft order exposure and aging for all customers.
            for order in orders_result.get("data", []):
                customer = order.get("customer", "Unknown")
                order_status = (order.get("status") or "").lower()
                if customer not in customer_outstanding:
                    customer_outstanding[customer] = {
                        "total_outstanding": 0,
                        "max_overdue_days": 0,
                        "draft_exposure": 0,
                        "invoices": [],
                        "orders": [order]
                    }
                else:
                    if "orders" not in customer_outstanding[customer]:
                        customer_outstanding[customer]["orders"] = []
                    customer_outstanding[customer]["orders"].append(order)

                # Draft orders indicate pipeline exposure and operational delay.
                if order_status == "draft":
                    order_amount = self._to_number(order.get("grand_total", 0))
                    customer_outstanding[customer]["draft_exposure"] = (
                        customer_outstanding[customer].get("draft_exposure", 0) + order_amount
                    )
                    customer_outstanding[customer]["total_outstanding"] += order_amount

                    order_date = self._parse_date(order.get("transaction_date") or order.get("delivery_date"))
                    order_age_days = max(0, (today - order_date).days) if order_date else 0
                    if order_age_days > customer_outstanding[customer]["max_overdue_days"]:
                        customer_outstanding[customer]["max_overdue_days"] = order_age_days
            
            # Analyze each customer
            for customer, data in customer_outstanding.items():
                amount_due = data["total_outstanding"]
                days_overdue = data["max_overdue_days"]
                
                # Skip if no outstanding amount and no significant age
                if amount_due <= 0 and days_overdue <= 0:
                    continue
                
                # Classify risk
                risk_level = self.classify_risk(amount_due, days_overdue)
                reasoning = self.get_reasoning(risk_level, amount_due, days_overdue)
                actions = self.get_suggested_actions(risk_level, customer)
                
                analysis = {
                    "id": str(uuid.uuid4()),
                    "customer": customer,
                    "amount_due": amount_due,
                    "days_overdue": days_overdue,
                    "risk_level": risk_level.value,
                    "reasoning": reasoning,
                    "suggested_actions": actions,
                    "invoice_count": len(data.get("invoices", [])),
                    "order_count": len(data.get("orders", [])),
                    "analyzed_at": datetime.now(timezone.utc).isoformat()
                }
                
                analyzed_orders.append(analysis)
                
                # Auto-trigger critical reminder if CRITICAL
                if risk_level == RiskLevel.CRITICAL:
                    auto_action = await self._trigger_auto_action(
                        customer, amount_due, days_overdue, "send_critical_reminder"
                    )
                    if auto_action:
                        auto_actions_triggered.append(auto_action)
            
            # Sort by risk level (critical first)
            risk_order = {"critical": 0, "medium": 1, "low": 2}
            analyzed_orders.sort(key=lambda x: (risk_order.get(x["risk_level"], 3), -x["amount_due"]))
            
            # Summary stats
            critical_count = len([o for o in analyzed_orders if o["risk_level"] == "critical"])
            medium_count = len([o for o in analyzed_orders if o["risk_level"] == "medium"])
            low_count = len([o for o in analyzed_orders if o["risk_level"] == "low"])
            total_at_risk = sum(o["amount_due"] for o in analyzed_orders if o["risk_level"] in ["critical", "medium"])
            
            return {
                "status": "success",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_analyzed": len(analyzed_orders),
                    "critical_count": critical_count,
                    "medium_count": medium_count,
                    "low_count": low_count,
                    "total_amount_at_risk": total_at_risk,
                    "auto_actions_triggered": len(auto_actions_triggered)
                },
                "orders": analyzed_orders,
                "auto_actions": auto_actions_triggered
            }
            
        except Exception as e:
            logger.error(f"Error analyzing orders: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _trigger_auto_action(
        self, 
        customer: str, 
        amount_due: float, 
        days_overdue: int,
        action_id: str
    ) -> Dict[str, Any]:
        """Trigger automatic action for critical risk (no confirmation needed)."""
        try:
            action_record = {
                "id": str(uuid.uuid4()),
                "action_id": action_id,
                "customer": customer,
                "amount_due": amount_due,
                "days_overdue": days_overdue,
                "action_type": "auto_critical_reminder",
                "status": "executed",
                "triggered_at": datetime.now(timezone.utc),
                "is_automatic": True,
                "message": f"Critical payment reminder automatically sent to {customer} for ₹{amount_due:,.0f} overdue by {days_overdue} days"
            }
            
            await self.actions_collection.insert_one(action_record)
            
            logger.info(f"Auto-action triggered: {action_id} for {customer}")
            
            return {
                "action_id": action_id,
                "customer": customer,
                "message": action_record["message"],
                "triggered_at": action_record["triggered_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering auto action: {str(e)}")
            return None
    
    async def execute_action(
        self,
        action_id: str,
        customer: str,
        order_analysis_id: str,
        user_id: str,
        user_email: str,
        user_role: str,
        company: str = None
    ) -> Dict[str, Any]:
        """
        Execute a suggested action (with confirmation already provided).
        Logs to audit trail.
        """
        try:
            # Define action implementations (mocked)
            action_results = {
                "stop_sales": {
                    "success": True,
                    "message": f"Future sales blocked for {customer}. Sales team notified.",
                    "effect": "Customer marked as 'Sales Blocked' in system"
                },
                "schedule_management_review": {
                    "success": True,
                    "message": f"Senior Management Review scheduled for {customer}. Management team notified.",
                    "effect": "Review meeting scheduled, stakeholders notified via email"
                },
                "escalate_management": {
                    "success": True,
                    "message": f"Issue escalated to senior management for {customer}.",
                    "effect": "Management notification sent, tracking ticket created"
                },
                "send_critical_reminder": {
                    "success": True,
                    "message": f"Critical payment reminder sent to {customer}.",
                    "effect": "Email/SMS notification dispatched"
                },
                "send_reminder": {
                    "success": True,
                    "message": f"Payment reminder sent to {customer}.",
                    "effect": "Standard reminder email sent"
                },
                "escalate_tracking": {
                    "success": True,
                    "message": f"Tracking ticket created for {customer}.",
                    "effect": "Follow-up task assigned to accounts team"
                },
                "view_order": {
                    "success": True,
                    "message": "Order details retrieved.",
                    "effect": "No system changes"
                },
                "continue_workflow": {
                    "success": True,
                    "message": "Workflow continued.",
                    "effect": "Standard processing resumed"
                }
            }
            
            result = action_results.get(action_id, {
                "success": True,
                "message": f"Action {action_id} executed.",
                "effect": "Action completed"
            })
            
            # Log to actions collection
            action_record = {
                "id": str(uuid.uuid4()),
                "action_id": action_id,
                "order_analysis_id": order_analysis_id,
                "customer": customer,
                "executed_by": user_email,
                "executed_by_role": user_role,
                "company": company,
                "status": "success" if result["success"] else "failed",
                "result_message": result["message"],
                "effect": result["effect"],
                "executed_at": datetime.now(timezone.utc),
                "is_automatic": False
            }
            
            await self.actions_collection.insert_one(action_record)
            
            # Log to audit trail
            await audit_service.log_action(
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                action=AuditAction.RUN_TOOL,
                resource_type="AIRiskAction",
                resource_id=action_record["id"],
                input_params={
                    "action_id": action_id,
                    "customer": customer,
                    "order_analysis_id": order_analysis_id
                },
                result="success" if result["success"] else "failure",
                result_message=result["message"],
                company=company
            )
            
            return {
                "status": "success",
                "action_id": action_id,
                "customer": customer,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {"status": "error", "message": str(e)}


# Singleton instance
ai_risk_analysis = AIRiskAnalysisService()
