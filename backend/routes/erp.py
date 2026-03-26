"""ERP routes - Direct ERPNext endpoints."""
from fastapi import APIRouter, Depends
from typing import Optional

from models import Customer, SalesOrder
from services.erp_service import erp_service
from services.audit_service import audit_service
from routes.auth import get_current_user

router = APIRouter(tags=["erp"])


@router.get("/customer/{customer_name}")
async def get_customer(customer_name: str):
    """Check if a customer exists."""
    result = await erp_service.check_customer(customer_name)
    return result


@router.post("/customer")
async def create_customer_endpoint(customer: Customer, user: Optional[dict] = Depends(get_current_user)):
    """Create a new customer."""
    result = await erp_service.create_customer(customer)

    if result.get("status") == "success" and user:
        await audit_service.log_action(
            user_id=user.get("id"),
            user_email=user.get("email"),
            user_role=user.get("role"),
            action="create_customer",
            resource_type="Customer",
            resource_id=result.get("data", {}).get("name"),
            input_params={"customer_name": customer.customer_name, "customer_type": customer.customer_type},
            result="success"
        )

    return result


@router.post("/sales-order")
async def create_sales_order_endpoint(sales_order: SalesOrder, user: Optional[dict] = Depends(get_current_user)):
    """Create a new sales order."""
    result = await erp_service.create_sales_order(sales_order)

    if result.get("status") == "success" and user:
        await audit_service.log_action(
            user_id=user.get("id"),
            user_email=user.get("email"),
            user_role=user.get("role"),
            action="create_order",
            resource_type="Sales Order",
            resource_id=result.get("data", {}).get("name"),
            input_params={"customer": sales_order.customer, "total": sales_order.items and sum([i.qty for i in sales_order.items])},
            result="success"
        )

    return result


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AgentERP API is running", "version": "1.0.0"}


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "erp_mode": "mock" if erp_service.mock_mode else "live",
        "erp_url": erp_service.base_url
    }
