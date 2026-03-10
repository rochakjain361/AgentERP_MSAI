"""Agent routes - Handles AI chat and agent orchestration."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

from models import ChatRequest, AgentRequest, AgentResponse, Customer, SalesOrder, SalesOrderItem
from services.erp_service import erp_service
from services.ai_service import ai_service

router = APIRouter(tags=["agent"])


@router.post("/chat", response_model=AgentResponse)
async def ai_chat(request: ChatRequest):
    """AI-powered chat endpoint that uses GPT to understand natural language and execute ERP operations."""
    try:
        message_lower = request.message.lower()
        
        # Direct pattern matching to bypass AI for common requests
        if any(term in message_lower for term in ['comprehensive analytics', 'detailed analytics', 'insights', 'full report', 'analytics and insights']):
            result = await erp_service.get_comprehensive_analytics()
            if result["status"] == "success":
                return AgentResponse(
                    status="success",
                    message="Here's your comprehensive business analytics dashboard:",
                    data={"type": "comprehensive_analytics", **result.get("data", {})}
                )
            else:
                return AgentResponse(status="error", message=result.get("message"))
        
        if any(term in message_lower for term in ['dashboard stat', 'quick stat', 'overview', 'quick overview']):
            result = await erp_service.get_dashboard_stats()
            if result["status"] == "success":
                stats = result.get("data", {})
                stats_message = "📊 ERP Dashboard:\n"
                stats_message += f"• Customers: {stats.get('total_customers', 0)}\n"
                stats_message += f"• Sales Orders: {stats.get('total_sales_orders', 0)}\n"
                stats_message += f"• Invoices: {stats.get('total_invoices', 0)}\n"
                stats_message += f"• Items: {stats.get('total_items', 0)}"
                return AgentResponse(status="success", message=stats_message, data={"type": "dashboard", **stats})
        
        # Use AI to parse natural language
        ai_result = await ai_service.parse_natural_language(request.message, request.conversation_history)
        
        if ai_result["status"] == "error":
            return AgentResponse(status="error", message=ai_result["message"])
        
        parsed_intent = ai_result["parsed_intent"]
        intent = parsed_intent.get("intent")
        natural_response = parsed_intent.get("natural_response", "")
        
        if intent == "general_query":
            return AgentResponse(status="success", message=natural_response, data=None)
        
        # Execute ERP operations based on intent
        if intent == "create_sales_order":
            customer_check = await erp_service.check_customer(parsed_intent.get("customer"))
            if not customer_check.get("exists"):
                return AgentResponse(
                    status="error",
                    message=f"Customer '{parsed_intent.get('customer')}' not found. Please check the customer name or create them first."
                )
            
            sales_order = SalesOrder(
                customer=parsed_intent.get("customer"),
                transaction_date=parsed_intent.get("transaction_date", datetime.now().strftime("%Y-%m-%d")),
                items=[SalesOrderItem(**item) for item in parsed_intent.get("items", [])]
            )
            result = await erp_service.create_sales_order(sales_order)
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
            customer_obj = Customer(**customer_data)
            result = await erp_service.create_customer(customer_obj)
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
async def agent_orchestration(request: AgentRequest):
    """Main orchestration endpoint for AI agent requests."""
    try:
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
            result = await erp_service.create_sales_order(sales_order)
            
            if result["status"] == "success":
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
            return AgentResponse(status=result["status"], message=result["message"], data=result.get("data"))
        
        else:
            return AgentResponse(status="error", message=f"Unknown intent: {request.intent}")
    
    except Exception as e:
        logging.error(f"Error in agent orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
