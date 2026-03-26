"""
Reasoning Engine - Analyzes ERP data and generates structured reasoning summaries.

This engine implements the analyze → classify → suggest workflow:
1. Detect situations from ERP data
2. Analyze relevant metrics
3. Classify severity based on thresholds
4. Generate actionable suggestions
5. Determine approval requirements
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

from services.erp_service import erp_service
from services.erp_entity_service import erp_entity_service

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SituationType(str, Enum):
    PAYMENT_DELAY = "payment_delay"
    HIGH_VALUE_ORDER = "high_value_order"
    INVENTORY_LOW = "inventory_low"
    CUSTOMER_CHURN_RISK = "customer_churn_risk"
    ORDER_BOTTLENECK = "order_bottleneck"
    REVENUE_OPPORTUNITY = "revenue_opportunity"
    DRAFT_ORDER_AGING = "draft_order_aging"
    CUSTOMER_CONCENTRATION = "customer_concentration"


# Threshold configurations
THRESHOLDS = {
    "payment_delay": {
        "critical_days": 60,
        "high_days": 45,
        "medium_days": 30,
        "critical_amount": 100000,
        "high_amount": 50000,
    },
    "high_value_order": {
        "approval_threshold": 50000,
        "critical_threshold": 200000,
    },
    "inventory": {
        "critical_stock_days": 3,
        "low_stock_days": 7,
    },
    "draft_order_aging": {
        "critical_days": 14,
        "high_days": 7,
        "medium_days": 3,
    },
    "customer_concentration": {
        "high_concentration_pct": 50,  # Single customer > 50% of revenue
        "medium_concentration_pct": 30,
    }
}


class ReasoningEngine:
    """Engine for proactive analysis and reasoning."""
    
    async def analyze_payment_delays(self, company_filter: str = None) -> List[Dict[str, Any]]:
        """
        Analyze customer payment delays and generate reasoning summaries.
        
        Hero Scenario: Delayed Payment Risk & Automated Intervention
        """
        try:
            situations = []
            
            # Get overdue invoices
            invoices_result = await erp_entity_service.query(
                doctype="Sales Invoice",
                filters=[
                    ["outstanding_amount", ">", 0],
                    ["docstatus", "=", 1]  # Submitted invoices
                ],
                fields=["name", "customer", "grand_total", "outstanding_amount", 
                        "due_date", "posting_date", "status"],
                limit=50,
                company_filter=company_filter
            )
            
            if invoices_result["status"] != "success":
                return []
            
            # Group by customer and analyze
            customer_data = {}
            today = datetime.now(timezone.utc).date()
            
            for invoice in invoices_result.get("data", []):
                customer = invoice.get("customer", "Unknown")
                
                if customer not in customer_data:
                    customer_data[customer] = {
                        "invoices": [],
                        "total_outstanding": 0,
                        "max_overdue_days": 0,
                        "oldest_invoice": None
                    }
                
                customer_data[customer]["invoices"].append(invoice)
                customer_data[customer]["total_outstanding"] += invoice.get("outstanding_amount", 0)
                
                # Calculate overdue days
                due_date_str = invoice.get("due_date")
                if due_date_str:
                    try:
                        if isinstance(due_date_str, str):
                            due_date = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                        else:
                            due_date = due_date_str
                        
                        overdue_days = (today - due_date).days
                        if overdue_days > 0:
                            if overdue_days > customer_data[customer]["max_overdue_days"]:
                                customer_data[customer]["max_overdue_days"] = overdue_days
                                customer_data[customer]["oldest_invoice"] = invoice.get("name")
                    except Exception as e:
                        logger.warning(f"Date parse error: {e}")
            
            # Generate reasoning for each customer with delays
            for customer, data in customer_data.items():
                if data["max_overdue_days"] > 0:
                    situation = await self._generate_payment_delay_reasoning(
                        customer, data, company_filter
                    )
                    if situation:
                        situations.append(situation)
            
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            situations.sort(key=lambda x: severity_order.get(x["severity"], 4))
            
            return situations[:10]  # Top 10 situations
            
        except Exception as e:
            logger.error(f"Error analyzing payment delays: {str(e)}")
            return []
    
    async def _generate_payment_delay_reasoning(
        self, 
        customer: str, 
        data: Dict, 
        company_filter: str = None
    ) -> Optional[Dict[str, Any]]:
        """Generate structured reasoning for a payment delay situation."""
        
        overdue_days = data["max_overdue_days"]
        outstanding = data["total_outstanding"]
        invoice_count = len(data["invoices"])
        
        # Classify severity
        severity = self._classify_payment_severity(overdue_days, outstanding)
        
        if severity == SeverityLevel.INFO:
            return None  # Skip non-actionable situations
        
        # Build metrics checked
        metrics_checked = [
            {"name": "Overdue Days", "value": overdue_days, "threshold": f">{THRESHOLDS['payment_delay']['medium_days']} days"},
            {"name": "Outstanding Amount", "value": f"₹{outstanding:,.2f}", "threshold": f">₹{THRESHOLDS['payment_delay']['high_amount']:,}"},
            {"name": "Open Invoices", "value": invoice_count, "threshold": "N/A"},
        ]
        
        # Get customer payment history (simplified)
        payment_history = await self._get_payment_history_summary(customer)
        if payment_history:
            metrics_checked.append({
                "name": "Payment History",
                "value": payment_history["summary"],
                "threshold": "Track record"
            })
        
        # Determine suggested actions based on severity
        suggested_actions = self._get_suggested_actions(severity, overdue_days, outstanding)
        
        # Determine if approval needed
        approval_needed = severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        
        # Calculate expected impact
        expected_impact = self._calculate_expected_impact(outstanding, overdue_days)
        
        # Build the reasoning summary
        reasoning = {
            "id": str(uuid.uuid4()),
            "type": SituationType.PAYMENT_DELAY.value,
            "severity": severity.value,
            "customer": customer,
            "company": company_filter,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            
            # Reasoning Summary
            "situation": f"Payment delay risk detected for {customer}",
            "status_reason": self._get_status_reason(severity, overdue_days, outstanding),
            
            # Metrics
            "metrics_checked": metrics_checked,
            
            # Actions
            "suggested_actions": suggested_actions,
            "approval_needed": approval_needed,
            "approval_reason": "Critical financial impact requires manager review" if approval_needed else None,
            
            # Impact
            "expected_impact": expected_impact,
            
            # Raw data for execution
            "context_data": {
                "customer": customer,
                "outstanding_amount": outstanding,
                "overdue_days": overdue_days,
                "invoice_count": invoice_count,
                "oldest_invoice": data.get("oldest_invoice"),
                "invoices": [inv.get("name") for inv in data["invoices"]]
            }
        }
        
        return reasoning
    
    def _classify_payment_severity(self, overdue_days: int, outstanding: float) -> SeverityLevel:
        """Classify severity based on overdue days and amount."""
        thresholds = THRESHOLDS["payment_delay"]
        
        # Critical: >60 days OR >₹1L outstanding
        if overdue_days >= thresholds["critical_days"] or outstanding >= thresholds["critical_amount"]:
            return SeverityLevel.CRITICAL
        
        # High: >45 days OR >₹50K outstanding
        if overdue_days >= thresholds["high_days"] or outstanding >= thresholds["high_amount"]:
            return SeverityLevel.HIGH
        
        # Medium: >30 days
        if overdue_days >= thresholds["medium_days"]:
            return SeverityLevel.MEDIUM
        
        # Low: Any overdue
        if overdue_days > 0:
            return SeverityLevel.LOW
        
        return SeverityLevel.INFO
    
    def _get_status_reason(self, severity: SeverityLevel, overdue_days: int, outstanding: float) -> str:
        """Get human-readable status reason."""
        reasons = {
            SeverityLevel.CRITICAL: f"CRITICAL: Payment overdue by {overdue_days} days with ₹{outstanding:,.0f} outstanding. Immediate action required.",
            SeverityLevel.HIGH: f"HIGH RISK: Payment delayed {overdue_days} days. Outstanding: ₹{outstanding:,.0f}. Escalation recommended.",
            SeverityLevel.MEDIUM: f"ATTENTION: Payment {overdue_days} days overdue. Monitor closely.",
            SeverityLevel.LOW: f"WATCH: Payment slightly delayed ({overdue_days} days).",
        }
        return reasons.get(severity, "Status unknown")
    
    def _get_suggested_actions(
        self, 
        severity: SeverityLevel, 
        overdue_days: int, 
        outstanding: float
    ) -> List[Dict[str, Any]]:
        """Get suggested actions based on severity."""
        
        actions = []
        
        if severity == SeverityLevel.CRITICAL:
            actions = [
                {
                    "id": "send_escalation",
                    "label": "Send Escalation Notice",
                    "description": "Send formal escalation notice to customer",
                    "action_type": "notification",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 1
                },
                {
                    "id": "raise_alert",
                    "label": "Raise Critical Alert",
                    "description": "Create critical alert in system for tracking",
                    "action_type": "alert",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 2
                },
                {
                    "id": "block_sales",
                    "label": "Block Further Sales",
                    "description": "Block new sales orders for this customer",
                    "action_type": "restriction",
                    "requires_approval": True,
                    "risk_level": "high",
                    "sequence_order": 3
                },
                {
                    "id": "notify_manager",
                    "label": "Notify Level 1 Manager",
                    "description": "Send notification to management for review",
                    "action_type": "notification",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 4
                }
            ]
        elif severity == SeverityLevel.HIGH:
            actions = [
                {
                    "id": "send_reminder",
                    "label": "Send Payment Reminder",
                    "description": "Send formal payment reminder to customer",
                    "action_type": "notification",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 1
                },
                {
                    "id": "raise_alert",
                    "label": "Raise High Priority Alert",
                    "description": "Create high-priority alert for tracking",
                    "action_type": "alert",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 2
                },
                {
                    "id": "notify_manager",
                    "label": "Notify Manager",
                    "description": "Alert manager about payment delay",
                    "action_type": "notification",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 3
                }
            ]
        elif severity == SeverityLevel.MEDIUM:
            actions = [
                {
                    "id": "send_reminder",
                    "label": "Send Gentle Reminder",
                    "description": "Send friendly payment reminder",
                    "action_type": "notification",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 1
                },
                {
                    "id": "log_followup",
                    "label": "Schedule Follow-up",
                    "description": "Create follow-up task for 7 days",
                    "action_type": "task",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 2
                }
            ]
        else:
            actions = [
                {
                    "id": "monitor",
                    "label": "Add to Watch List",
                    "description": "Add customer to payment watch list",
                    "action_type": "tracking",
                    "requires_approval": False,
                    "risk_level": "low",
                    "sequence_order": 1
                }
            ]
        
        return actions
    
    async def _get_payment_history_summary(self, customer: str) -> Optional[Dict[str, Any]]:
        """Get customer's payment history summary."""
        try:
            # Query past paid invoices
            result = await erp_entity_service.query(
                doctype="Sales Invoice",
                filters=[
                    ["customer", "=", customer],
                    ["status", "=", "Paid"]
                ],
                fields=["name", "grand_total", "posting_date"],
                limit=10
            )
            
            if result["status"] == "success" and result["count"] > 0:
                total_paid = sum(inv.get("grand_total", 0) for inv in result["data"])
                return {
                    "paid_invoices": result["count"],
                    "total_paid": total_paid,
                    "summary": f"{result['count']} invoices paid (₹{total_paid:,.0f} total)"
                }
            return {"summary": "No payment history available"}
        except Exception:
            return None
    
    def _calculate_expected_impact(self, outstanding: float, overdue_days: int) -> Dict[str, Any]:
        """Calculate expected business impact of intervention."""
        
        # Cost of capital (assume 12% annual)
        daily_cost = outstanding * 0.12 / 365
        cost_incurred = daily_cost * overdue_days
        
        # Estimated recovery improvement with intervention
        recovery_probability = 0.7 if overdue_days < 60 else 0.4
        expected_recovery = outstanding * recovery_probability
        
        # Time saved vs manual follow-up
        manual_hours = 2.5  # Hours for manual follow-up
        automated_hours = 0.25  # Hours with automation
        time_saved = manual_hours - automated_hours
        
        return {
            "financial_risk": outstanding,
            "cost_of_delay_per_day": round(daily_cost, 2),
            "cost_incurred": round(cost_incurred, 2),
            "expected_recovery": round(expected_recovery, 2),
            "recovery_probability": f"{int(recovery_probability * 100)}%",
            "time_saved_hours": time_saved,
            "consultant_hours_avoided": manual_hours,
            "risk_reduction": "High" if overdue_days >= 60 else "Medium"
        }
    
    async def analyze_high_value_orders(self, company_filter: str = None) -> List[Dict[str, Any]]:
        """Analyze high-value orders that may need attention."""
        try:
            situations = []
            
            result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[["status", "=", "Draft"]],
                fields=["name", "customer", "grand_total", "transaction_date", "status"],
                limit=20,
                company_filter=company_filter
            )
            
            if result["status"] != "success":
                return []
            
            for order in result.get("data", []):
                grand_total = order.get("grand_total", 0)
                
                if grand_total >= THRESHOLDS["high_value_order"]["approval_threshold"]:
                    severity = SeverityLevel.CRITICAL if grand_total >= THRESHOLDS["high_value_order"]["critical_threshold"] else SeverityLevel.HIGH
                    
                    situations.append({
                        "id": str(uuid.uuid4()),
                        "type": SituationType.HIGH_VALUE_ORDER.value,
                        "severity": severity.value,
                        "customer": order.get("customer"),
                        "company": company_filter,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        
                        "situation": f"High-value order pending for {order.get('customer')}",
                        "status_reason": f"Order worth ₹{grand_total:,.0f} in Draft status requires processing",
                        
                        "metrics_checked": [
                            {"name": "Order Value", "value": f"₹{grand_total:,.0f}", "threshold": f">₹{THRESHOLDS['high_value_order']['approval_threshold']:,}"},
                            {"name": "Status", "value": "Draft", "threshold": "Pending submission"},
                        ],
                        
                        "suggested_actions": [
                            {
                                "id": "submit_order",
                                "label": "Submit Order",
                                "description": "Submit the sales order for processing",
                                "action_type": "workflow",
                                "requires_approval": True,
                                "risk_level": "medium",
                                "sequence_order": 1
                            },
                            {
                                "id": "verify_customer",
                                "label": "Verify Customer Credit",
                                "description": "Check customer credit status before processing",
                                "action_type": "validation",
                                "requires_approval": False,
                                "risk_level": "low",
                                "sequence_order": 0
                            }
                        ],
                        
                        "approval_needed": True,
                        "approval_reason": f"High-value order (₹{grand_total:,.0f}) requires manager approval",
                        
                        "expected_impact": {
                            "financial_value": grand_total,
                            "revenue_at_stake": grand_total,
                            "time_saved_hours": 1.5,
                        },
                        
                        "context_data": {
                            "order_name": order.get("name"),
                            "customer": order.get("customer"),
                            "grand_total": grand_total,
                            "status": order.get("status")
                        }
                    })
            
            return situations
            
        except Exception as e:
            logger.error(f"Error analyzing high-value orders: {str(e)}")
            return []
    
    async def get_todays_priorities(
        self, 
        user_role: str, 
        company_filter: str = None
    ) -> Dict[str, Any]:
        """
        Get today's priorities - the main entry point for proactive analysis.
        Returns all situations requiring attention.
        """
        try:
            all_situations = []
            
            # 1. Payment delays (hero scenario)
            payment_situations = await self.analyze_payment_delays(company_filter)
            all_situations.extend(payment_situations)
            
            # 2. High-value orders
            order_situations = await self.analyze_high_value_orders(company_filter)
            all_situations.extend(order_situations)
            
            # 3. Draft order aging
            aging_situations = await self.analyze_draft_order_aging(company_filter)
            all_situations.extend(aging_situations)
            
            # 4. Customer concentration risk
            concentration_situations = await self.analyze_customer_concentration(company_filter)
            all_situations.extend(concentration_situations)
            
            # 5. Revenue opportunities
            opportunity_situations = await self.analyze_revenue_opportunities(company_filter)
            all_situations.extend(opportunity_situations)
            
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            all_situations.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 4))
            
            # Summary stats
            critical_count = len([s for s in all_situations if s.get("severity") == "critical"])
            high_count = len([s for s in all_situations if s.get("severity") == "high"])
            medium_count = len([s for s in all_situations if s.get("severity") == "medium"])
            
            return {
                "status": "success",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "user_role": user_role,
                "company": company_filter,
                "summary": {
                    "total_situations": len(all_situations),
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "requires_immediate_attention": critical_count > 0,
                    "headline": f"{critical_count} critical, {high_count} high priority items" if critical_count + high_count > 0 else "No urgent items"
                },
                "situations": all_situations[:15]  # Top 15
            }
            
        except Exception as e:
            logger.error(f"Error getting today's priorities: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_draft_order_aging(self, company_filter: str = None) -> List[Dict[str, Any]]:
        """Analyze draft orders that have been pending too long."""
        try:
            situations = []
            today = datetime.now(timezone.utc).date()
            
            result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[["status", "=", "Draft"]],
                fields=["name", "customer", "grand_total", "transaction_date", "status"],
                limit=50,
                company_filter=company_filter
            )
            
            if result["status"] != "success":
                return []
            
            for order in result.get("data", []):
                trans_date_str = order.get("transaction_date")
                if not trans_date_str:
                    continue
                
                try:
                    if isinstance(trans_date_str, str):
                        trans_date = datetime.strptime(trans_date_str[:10], "%Y-%m-%d").date()
                    else:
                        trans_date = trans_date_str
                    
                    age_days = (today - trans_date).days
                    grand_total = order.get("grand_total", 0)
                    
                    # Only flag if aging > 3 days
                    if age_days < THRESHOLDS["draft_order_aging"]["medium_days"]:
                        continue
                    
                    # Classify severity
                    if age_days >= THRESHOLDS["draft_order_aging"]["critical_days"]:
                        severity = SeverityLevel.CRITICAL
                    elif age_days >= THRESHOLDS["draft_order_aging"]["high_days"]:
                        severity = SeverityLevel.HIGH
                    else:
                        severity = SeverityLevel.MEDIUM
                    
                    situations.append({
                        "id": str(uuid.uuid4()),
                        "type": SituationType.DRAFT_ORDER_AGING.value,
                        "severity": severity.value,
                        "customer": order.get("customer"),
                        "company": company_filter,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        
                        "situation": f"Draft order aging for {order.get('customer')}",
                        "status_reason": f"Order {order.get('name')} worth ₹{grand_total:,.0f} has been in draft for {age_days} days",
                        
                        "metrics_checked": [
                            {"name": "Order Age", "value": f"{age_days} days", "threshold": f">{THRESHOLDS['draft_order_aging']['medium_days']} days"},
                            {"name": "Order Value", "value": f"₹{grand_total:,.0f}", "threshold": "N/A"},
                            {"name": "Status", "value": "Draft", "threshold": "Should be Submitted"},
                        ],
                        
                        "suggested_actions": [
                            {
                                "id": "contact_customer",
                                "label": "Contact Customer",
                                "description": f"Follow up with {order.get('customer')} to confirm order",
                                "action_type": "communication",
                                "requires_approval": False,
                                "risk_level": "low",
                                "sequence_order": 1
                            },
                            {
                                "id": "submit_order",
                                "label": "Submit Order",
                                "description": "Submit the order for processing",
                                "action_type": "workflow",
                                "requires_approval": grand_total > 5000,
                                "risk_level": "medium",
                                "sequence_order": 2
                            },
                            {
                                "id": "cancel_order",
                                "label": "Cancel if Unresponsive",
                                "description": "Cancel order if customer doesn't respond",
                                "action_type": "workflow",
                                "requires_approval": True,
                                "risk_level": "medium",
                                "sequence_order": 3
                            }
                        ],
                        
                        "approval_needed": grand_total > 5000,
                        "approval_reason": f"High-value order (₹{grand_total:,.0f}) requires approval" if grand_total > 5000 else None,
                        
                        "expected_impact": {
                            "revenue_at_risk": grand_total,
                            "potential_loss_per_day": grand_total * 0.001,  # 0.1% per day opportunity cost
                            "time_saved_hours": 1.0,
                            "risk_reduction": "High" if age_days >= 14 else "Medium"
                        },
                        
                        "context_data": {
                            "order_name": order.get("name"),
                            "customer": order.get("customer"),
                            "grand_total": grand_total,
                            "age_days": age_days,
                            "transaction_date": trans_date_str
                        }
                    })
                    
                except Exception as e:
                    logger.warning(f"Date parse error for order: {e}")
            
            return situations
            
        except Exception as e:
            logger.error(f"Error analyzing draft order aging: {str(e)}")
            return []
    
    async def analyze_customer_concentration(self, company_filter: str = None) -> List[Dict[str, Any]]:
        """Analyze revenue concentration risk across customers."""
        try:
            situations = []
            
            # Get all orders to calculate revenue by customer
            result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[],
                fields=["name", "customer", "grand_total", "status"],
                limit=100,
                company_filter=company_filter
            )
            
            if result["status"] != "success" or result["count"] < 2:
                return []
            
            # Calculate revenue by customer
            customer_revenue = {}
            total_revenue = 0
            
            for order in result.get("data", []):
                customer = order.get("customer", "Unknown")
                amount = order.get("grand_total", 0)
                customer_revenue[customer] = customer_revenue.get(customer, 0) + amount
                total_revenue += amount
            
            if total_revenue == 0:
                return []
            
            # Check for concentration risk
            for customer, revenue in customer_revenue.items():
                concentration_pct = (revenue / total_revenue) * 100
                
                if concentration_pct >= THRESHOLDS["customer_concentration"]["high_concentration_pct"]:
                    severity = SeverityLevel.HIGH
                elif concentration_pct >= THRESHOLDS["customer_concentration"]["medium_concentration_pct"]:
                    severity = SeverityLevel.MEDIUM
                else:
                    continue  # Not a concentration risk
                
                situations.append({
                    "id": str(uuid.uuid4()),
                    "type": SituationType.CUSTOMER_CONCENTRATION.value,
                    "severity": severity.value,
                    "customer": customer,
                    "company": company_filter,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    
                    "situation": f"High revenue concentration on {customer}",
                    "status_reason": f"{customer} accounts for {concentration_pct:.0f}% of total revenue (₹{revenue:,.0f} of ₹{total_revenue:,.0f})",
                    
                    "metrics_checked": [
                        {"name": "Revenue Share", "value": f"{concentration_pct:.1f}%", "threshold": f">{THRESHOLDS['customer_concentration']['medium_concentration_pct']}%"},
                        {"name": "Customer Revenue", "value": f"₹{revenue:,.0f}", "threshold": "N/A"},
                        {"name": "Total Revenue", "value": f"₹{total_revenue:,.0f}", "threshold": "N/A"},
                        {"name": "Customer Count", "value": len(customer_revenue), "threshold": "Diversification needed"},
                    ],
                    
                    "suggested_actions": [
                        {
                            "id": "diversify_pipeline",
                            "label": "Diversify Sales Pipeline",
                            "description": "Initiate outreach to acquire new customers",
                            "action_type": "strategy",
                            "requires_approval": False,
                            "risk_level": "low",
                            "sequence_order": 1
                        },
                        {
                            "id": "strengthen_relationship",
                            "label": "Strengthen Key Relationship",
                            "description": f"Schedule review meeting with {customer}",
                            "action_type": "communication",
                            "requires_approval": False,
                            "risk_level": "low",
                            "sequence_order": 2
                        },
                        {
                            "id": "risk_assessment",
                            "label": "Conduct Risk Assessment",
                            "description": "Evaluate dependency and create mitigation plan",
                            "action_type": "analysis",
                            "requires_approval": False,
                            "risk_level": "low",
                            "sequence_order": 3
                        }
                    ],
                    
                    "approval_needed": False,
                    
                    "expected_impact": {
                        "revenue_at_risk": revenue,
                        "concentration_percentage": concentration_pct,
                        "risk_reduction": "High" if concentration_pct >= 50 else "Medium"
                    },
                    
                    "context_data": {
                        "customer": customer,
                        "customer_revenue": revenue,
                        "total_revenue": total_revenue,
                        "concentration_pct": concentration_pct,
                        "customer_count": len(customer_revenue)
                    }
                })
            
            return situations[:3]  # Top 3 concentration risks
            
        except Exception as e:
            logger.error(f"Error analyzing customer concentration: {str(e)}")
            return []
    
    async def analyze_revenue_opportunities(self, company_filter: str = None) -> List[Dict[str, Any]]:
        """Identify revenue growth opportunities."""
        try:
            situations = []
            
            # Get draft orders for quick wins
            orders_result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[["status", "=", "Draft"]],
                fields=["name", "customer", "grand_total", "status"],
                limit=50,
                company_filter=company_filter
            )
            
            if orders_result["status"] == "success" and orders_result["count"] > 0:
                total_draft_value = sum(o.get("grand_total", 0) for o in orders_result["data"])
                draft_count = orders_result["count"]
                
                if total_draft_value > 0:
                    situations.append({
                        "id": str(uuid.uuid4()),
                        "type": SituationType.REVENUE_OPPORTUNITY.value,
                        "severity": SeverityLevel.MEDIUM.value,
                        "customer": "Multiple Customers",
                        "company": company_filter,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        
                        "situation": f"₹{total_draft_value:,.0f} revenue pending in {draft_count} draft orders",
                        "status_reason": f"Quick win opportunity: Convert {draft_count} draft orders to capture ₹{total_draft_value:,.0f} in revenue",
                        
                        "metrics_checked": [
                            {"name": "Draft Orders", "value": draft_count, "threshold": "Should be 0"},
                            {"name": "Pending Revenue", "value": f"₹{total_draft_value:,.0f}", "threshold": "Opportunity"},
                            {"name": "Avg Order Value", "value": f"₹{total_draft_value/draft_count:,.0f}", "threshold": "N/A"},
                        ],
                        
                        "suggested_actions": [
                            {
                                "id": "review_drafts",
                                "label": "Review All Draft Orders",
                                "description": "Prioritize and process pending draft orders",
                                "action_type": "workflow",
                                "requires_approval": False,
                                "risk_level": "low",
                                "sequence_order": 1
                            },
                            {
                                "id": "batch_submit",
                                "label": "Batch Submit Orders",
                                "description": "Submit all verified orders in one action",
                                "action_type": "workflow",
                                "requires_approval": True,
                                "risk_level": "medium",
                                "sequence_order": 2
                            },
                            {
                                "id": "notify_team",
                                "label": "Notify Sales Team",
                                "description": "Alert team about pending opportunities",
                                "action_type": "notification",
                                "requires_approval": False,
                                "risk_level": "low",
                                "sequence_order": 3
                            }
                        ],
                        
                        "approval_needed": True,
                        "approval_reason": "Batch submission requires manager approval",
                        
                        "expected_impact": {
                            "potential_revenue": total_draft_value,
                            "orders_to_process": draft_count,
                            "time_saved_hours": draft_count * 0.5,  # 30 mins per order
                            "conversion_rate_target": "100%"
                        },
                        
                        "context_data": {
                            "draft_count": draft_count,
                            "total_draft_value": total_draft_value,
                            "orders": [o.get("name") for o in orders_result["data"]]
                        }
                    })
            
            return situations
            
        except Exception as e:
            logger.error(f"Error analyzing revenue opportunities: {str(e)}")
            return []


# Singleton instance
reasoning_engine = ReasoningEngine()
