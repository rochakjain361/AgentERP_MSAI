"""Agent routes - Handles AI chat and agent orchestration with RBAC."""
from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime
from typing import Optional
import logging

from models import ChatRequest, AgentRequest, AgentResponse, Customer, SalesOrder, SalesOrderItem
from services.erp_service import erp_service
from services.ai_service import ai_service
from services.audit_service import audit_service
from services.approval_service import approval_service
from models.enterprise import AuditAction
from routes.auth import get_current_user, require_auth

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


# Access Level Definitions
# Level 1 (Admin): Create, Edit, Delete, View + Approve for Level 2
# Level 2 (Manager/Operator): Create, View + Approve for Level 3
# Level 3 (Viewer): View only

ACCESS_LEVELS = {
    "admin": 1,
    "manager": 2,
    "operator": 2,
    "viewer": 3
}

def get_access_level(role: str) -> int:
    return ACCESS_LEVELS.get(role, 3)

def can_create(role: str) -> bool:
    """Level 1 and 2 can create."""
    return get_access_level(role) <= 2

def can_view_only(role: str) -> bool:
    """Check if user is Level 3 (view only)."""
    return get_access_level(role) == 3


# List of create/edit intents that require Level 1 or 2
CREATE_EDIT_INTENTS = [
    "create_sales_order", "create_customer", "create_order",
    "update_order", "update_customer", "edit_order", "edit_customer",
    "delete_order", "delete_customer"
]

# Read-only intents allowed for all levels
VIEW_INTENTS = [
    "list_sales_orders", "list_invoices", "list_customers",
    "check_customer", "dashboard_stats", "comprehensive_analytics",
    "general_query"
]


@router.post("/chat", response_model=AgentResponse)
async def ai_chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    """AI-powered chat endpoint with RBAC enforcement."""
    try:
        message_lower = request.message.lower()
        
        # Check if user is authenticated
        user_id = user["id"] if user else "anonymous"
        user_email = user["email"] if user else "anonymous"
        user_role = user["role"] if user else "viewer"
        
        # Block create/edit actions for Level 3 (viewers)
        if user and can_view_only(user_role):
            # Check if message contains create/edit keywords
            create_keywords = ["create", "add", "new", "make", "insert", "update", "edit", "modify", "delete", "remove"]
            if any(keyword in message_lower for keyword in create_keywords):
                await audit_service.log_action(
                    user_id=user_id,
                    user_email=user_email,
                    user_role=user_role,
                    action=AuditAction.AI_CHAT,
                    resource_type="Chat",
                    result="failure",
                    result_message="Action blocked: Viewers cannot create/edit",
                    ai_reasoning="User attempted create/edit action with viewer role"
                )
                return AgentResponse(
                    status="error",
                    message="⚠️ Access Denied: As a Viewer (Level 3), you can only view data. Creating, editing, or deleting records requires Manager or Admin access.\n\nPlease contact your administrator to request elevated permissions."
                )
        
        # Direct pattern matching for common requests (allow for all roles)
        if any(term in message_lower for term in ['comprehensive analytics', 'detailed analytics', 'insights', 'full report', 'analytics and insights']):
            result = await erp_service.get_comprehensive_analytics()
            if result["status"] == "success":
                if user:
                    await audit_service.log_action(
                        user_id=user_id,
                        user_email=user_email,
                        user_role=user_role,
                        action=AuditAction.QUERY_DATA,
                        resource_type="Analytics",
                        result="success"
                    )
                return AgentResponse(
                    status="success",
                    message="Here's your comprehensive business analytics dashboard:",
                    data={"type": "comprehensive_analytics", **result.get("data", {})}
                )
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        if any(term in message_lower for term in ['dashboard stat', 'quick stat', 'overview', 'quick overview', 'show me the dashboard']):
            result = await erp_service.get_dashboard_stats()
            if result["status"] == "success":
                stats = result.get("data", {})
                stats_message = "📊 ERP Dashboard:\n"
                stats_message += f"• Customers: {stats.get('total_customers', 0)}\n"
                stats_message += f"• Sales Orders: {stats.get('total_sales_orders', 0)}\n"
                stats_message += f"• Invoices: {stats.get('total_invoices', 0)}\n"
                stats_message += f"• Items: {stats.get('total_items', 0)}"
                if user:
                    await audit_service.log_action(
                        user_id=user_id,
                        user_email=user_email,
                        user_role=user_role,
                        action=AuditAction.QUERY_DATA,
                        resource_type="Dashboard",
                        result="success"
                    )
                return AgentResponse(status="success", message=stats_message, data={"type": "dashboard", **stats})
        
        # Use AI to parse natural language
        ai_result = await ai_service.parse_natural_language(request.message, request.conversation_history)
        
        if ai_result["status"] == "error":
            return AgentResponse(status="error", message=ai_result["message"])
        
        parsed_intent = ai_result["parsed_intent"]
        intent = parsed_intent.get("intent")
        natural_response = parsed_intent.get("natural_response", "")
        
        # Log AI chat action
        if user:
            await audit_service.log_action(
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                action=AuditAction.AI_CHAT,
                resource_type="Chat",
                input_params={"message": request.message[:100], "intent": intent},
                result="success",
                ai_reasoning=f"Parsed intent: {intent}"
            )
        
        if intent == "general_query":
            return AgentResponse(status="success", message=natural_response, data=None)
        
        # Check permission for create/edit intents
        if intent in CREATE_EDIT_INTENTS:
            if user and can_view_only(user_role):
                return AgentResponse(
                    status="error",
                    message="⚠️ Access Denied: As a Viewer (Level 3), you cannot perform this action.\n\nRequired: Manager (Level 2) or Admin (Level 1) access."
                )
        
        # Execute ERP operations based on intent
        if intent == "create_sales_order":
            # Check for high-value order approval requirement
            items = parsed_intent.get("items", [])
            estimated_value = sum(item.get("qty", 1) * item.get("rate", 0) for item in items)
            
            if estimated_value > 50000 and user and user_role not in ["admin"]:
                # Requires approval
                approval_result = await approval_service.create_approval_request(
                    requester_id=user_id,
                    requester_email=user_email,
                    requester_role=user_role,
                    action_type=AuditAction.CREATE_ORDER,
                    resource_type="Sales Order",
                    resource_data={
                        "customer": parsed_intent.get("customer"),
                        "items": items,
                        "grand_total": estimated_value
                    },
                    rule_triggered="high_value_order",
                    reason=f"Order value ₹{estimated_value:,.2f} exceeds ₹50,000 threshold",
                    ai_analysis=f"AI detected high-value order creation request for {parsed_intent.get('customer')}"
                )
                
                return AgentResponse(
                    status="approval_required",
                    message=f"⏳ This order requires approval.\n\n**Reason:** Order value (₹{estimated_value:,.2f}) exceeds ₹50,000 threshold.\n\nYour request has been submitted for manager approval. You will be notified once it's reviewed.",
                    data={"approval_id": approval_result.get("approval_id")}
                )
            
            customer_name = parsed_intent.get("customer")
            
            # Check if customer exists
            customer_check = await erp_service.check_customer(customer_name)
            
            # If customer doesn't exist, create it automatically
            if not customer_check.get("exists"):
                logger.info(f"Customer '{customer_name}' not found. Creating automatically...")
                customer = Customer(
                    doctype="Customer",
                    customer_name=customer_name,
                    customer_type="Company",
                    territory="India"
                )
                create_result = await erp_service.create_customer(customer)
                if create_result["status"] != "success":
                    return AgentResponse(
                        status="error",
                        message=f"Failed to create customer '{customer_name}'. {create_result.get('message', '')}"
                    )
                logger.info(f"✓ Customer '{customer_name}' created successfully")
            
            sales_order = SalesOrder(
                customer=customer_name,
                transaction_date=parsed_intent.get("transaction_date", datetime.now().strftime("%Y-%m-%d")),
                items=[SalesOrderItem(**item) for item in parsed_intent.get("items", [])]
            )
            result = await erp_service.create_sales_order(sales_order, company=user.get("company") if user else None)
            
            if result["status"] == "success" and user:
                await audit_service.log_action(
                    user_id=user_id,
                    user_email=user_email,
                    user_role=user_role,
                    action=AuditAction.CREATE_ORDER,
                    resource_type="Sales Order",
                    resource_id=result.get("data", {}).get("name"),
                    result="success",
                    result_message=f"Created order for {parsed_intent.get('customer')}"
                )
            
            return AgentResponse(
                status=result["status"],
                message=natural_response if result["status"] == "success" else result["message"],
                data=result.get("data")
            )
        
        elif intent == "check_customer":
            result = await erp_service.check_customer(parsed_intent.get("customer"))
            if result["status"] == "success" and result.get("exists"):
                return AgentResponse(status="success", message=f"{natural_response}\n\nCustomer found in the system!", data=result.get("data"))
            elif result["status"] == "success":
                return AgentResponse(status="success", message=f"{natural_response}\n\nCustomer not found in the system.", data=None)
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        elif intent == "create_customer":
            customer_data = parsed_intent.get("customer_data", {})

            # Support chat-style fields with names like customer or name
            if not customer_data.get("customer_name"):
                customer_data["customer_name"] = parsed_intent.get("customer") or parsed_intent.get("name")
            if not customer_data.get("customer_name") and parsed_intent.get("customer_data"):
                # map any 'name' subfield
                customer_data["customer_name"] = parsed_intent.get("customer_data", {}).get("name")

            if not customer_data.get("customer_type"):
                customer_data["customer_type"] = parsed_intent.get("customer_type", "Company")
            if not customer_data.get("territory"):
                customer_data["territory"] = parsed_intent.get("territory", "India")

            customer_obj = Customer(**customer_data)
            result = await erp_service.create_customer(customer_obj)
            
            if result["status"] == "success" and user:
                await audit_service.log_action(
                    user_id=user_id,
                    user_email=user_email,
                    user_role=user_role,
                    action=AuditAction.CREATE_CUSTOMER,
                    resource_type="Customer",
                    resource_id=result.get("data", {}).get("name"),
                    result="success"
                )
            
            return AgentResponse(
                status=result["status"],
                message=natural_response if result["status"] == "success" else result["message"],
                data=result.get("data")
            )
        
        elif intent == "list_sales_orders":
            result = await erp_service.get_sales_orders(limit=10)
            if result["status"] == "success":
                return AgentResponse(status="success", message=natural_response, data={"type": "sales_orders_list", "orders": result.get("data", [])})
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        elif intent == "list_invoices":
            result = await erp_service.get_invoices(limit=10)
            if result["status"] == "success":
                return AgentResponse(status="success", message=natural_response, data={"type": "invoices_list", "invoices": result.get("data", [])})
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        elif intent == "list_customers":
            result = await erp_service.get_customers(limit=10)
            if result["status"] == "success":
                return AgentResponse(status="success", message=natural_response, data={"type": "customers_list", "customers": result.get("data", [])})
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        elif intent == "dashboard_stats":
            result = await erp_service.get_dashboard_stats()
            if result["status"] == "success":
                stats = result.get("data", {})
                stats_message = f"{natural_response}\n\n📊 ERP Dashboard:\n"
                stats_message += f"• Customers: {stats.get('total_customers', 0)}\n"
                stats_message += f"• Sales Orders: {stats.get('total_sales_orders', 0)}\n"
                stats_message += f"• Invoices: {stats.get('total_invoices', 0)}\n"
                stats_message += f"• Items: {stats.get('total_items', 0)}"
                return AgentResponse(status="success", message=stats_message, data={"type": "dashboard", **stats})
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        elif intent == "comprehensive_analytics":
            result = await erp_service.get_comprehensive_analytics()
            if result["status"] == "success":
                return AgentResponse(status="success", message=natural_response, data={"type": "comprehensive_analytics", **result.get("data", {})})
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        else:
            return AgentResponse(status="error", message=f"Unknown intent: {intent}")
    
    except Exception as e:
        logging.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent", response_model=AgentResponse)
async def agent_orchestration(request: AgentRequest, user: dict = Depends(require_auth)):
    """Main orchestration endpoint for AI agent requests (requires auth)."""
    try:
        # Check permissions for create/edit intents
        if request.intent in CREATE_EDIT_INTENTS and can_view_only(user["role"]):
            return AgentResponse(
                status="error",
                message="Access Denied: Viewers cannot perform create/edit operations."
            )
        
        if request.intent == "create_sales_order":
            customer_check = await erp_service.check_customer(request.customer)
            
            if not customer_check.get("exists"):
                customer_data = request.customer_data or {
                    "customer_name": request.customer,
                    "customer_type": "Company",
                    "territory": "India"
                }
                customer_obj = Customer(**customer_data)
                create_result = await erp_service.create_customer(customer_obj)
                
                if create_result["status"] != "success":
                    return AgentResponse(status="error", message=f"Failed to create customer: {create_result.get('message')}")
            
            sales_order = SalesOrder(
                customer=request.customer,
                transaction_date=request.transaction_date or datetime.now().strftime("%Y-%m-%d"),
                items=[SalesOrderItem(**item.model_dump()) for item in request.items]
            )
            result = await erp_service.create_sales_order(sales_order, company=user.get("company") if user else None)
            
            if result["status"] == "success":
                await audit_service.log_action(
                    user_id=user["id"],
                    user_email=user["email"],
                    user_role=user["role"],
                    action=AuditAction.CREATE_ORDER,
                    resource_type="Sales Order",
                    resource_id=result.get("data", {}).get("name"),
                    result="success"
                )
                return AgentResponse(status="success", message=result["message"], data=result["data"])
            else:
                return AgentResponse(status="error", message=result["message"])
        
        elif request.intent == "check_customer":
            result = await erp_service.check_customer(request.customer)
            if result["status"] == "success" and result.get("exists"):
                return AgentResponse(status="success", message=f"Customer found: {request.customer}", data=result.get("data"))
            elif result["status"] == "success":
                return AgentResponse(status="success", message=f"Customer '{request.customer}' not found", data=None)
            else:
                return AgentResponse(status="error", message=result.get("message", "Unknown error"))
        
        elif request.intent == "create_customer":
            customer_data = request.customer_data or {}
            customer_obj = Customer(**customer_data)
            result = await erp_service.create_customer(customer_obj)
            
            if result["status"] == "success":
                await audit_service.log_action(
                    user_id=user["id"],
                    user_email=user["email"],
                    user_role=user["role"],
                    action=AuditAction.CREATE_CUSTOMER,
                    resource_type="Customer",
                    resource_id=result.get("data", {}).get("name"),
                    result="success"
                )
            
            return AgentResponse(status=result["status"], message=result["message"], data=result.get("data"))
        
        else:
            return AgentResponse(status="error", message=f"Unknown intent: {request.intent}")
    
    except Exception as e:
        logging.error(f"Error in agent orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
