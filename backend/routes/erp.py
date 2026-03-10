"""ERP routes - Direct ERPNext endpoints."""
from fastapi import APIRouter

from models import Customer, SalesOrder
from services.erp_service import erp_service

router = APIRouter(tags=["erp"])


@router.get("/customer/{customer_name}")
async def get_customer(customer_name: str):
    """Check if a customer exists."""
    result = await erp_service.check_customer(customer_name)
    return result


@router.post("/customer")
async def create_customer_endpoint(customer: Customer):
    """Create a new customer."""
    result = await erp_service.create_customer(customer)
    return result


@router.post("/sales-order")
async def create_sales_order_endpoint(sales_order: SalesOrder):
    """Create a sales order."""
    result = await erp_service.create_sales_order(sales_order)
    return result


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AgentERP API is running", "version": "1.0.0"}


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    from database import is_mongodb_available

    return {
        "status": "healthy",
        "erp_mode": "mock" if erp_service.mock_mode else "live",
        "erp_url": erp_service.base_url,
        "database": "mongodb" if is_mongodb_available() else "in-memory"
    }
