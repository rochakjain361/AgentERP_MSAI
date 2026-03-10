"""Tools routes - Simple REST endpoints for custom tools."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import json

from services.tool_registry import tool_registry
from services.erp_entity_service import erp_entity_service

router = APIRouter(prefix="/tools", tags=["tools"])


class CreateToolRequest(BaseModel):
    """Request model for creating a tool."""
    tool_name: str = Field(..., description="Name of the tool")
    doctype: str = Field(..., description="ERPNext DocType")
    prompt: str = Field(..., description="Description/prompt for the tool")
    filters: Optional[List] = Field(None, description="Query filters")
    fields: Optional[List[str]] = Field(None, description="Fields to return")


@router.get("")
async def get_tools():
    """Get all saved tools."""
    result = await tool_registry.list_tools()
    return result


@router.post("")
async def create_tool(request: CreateToolRequest):
    """Create a new custom tool."""
    # Parse prompt to generate filters if not provided
    filters = request.filters
    if not filters:
        # Generate basic filters based on prompt keywords
        filters = parse_prompt_to_filters(request.prompt, request.doctype)
    
    # Default fields based on doctype
    fields = request.fields
    if not fields:
        fields = get_default_fields(request.doctype)
    
    result = await tool_registry.create_tool(
        tool_name=request.tool_name.lower().replace(" ", "_"),
        doctype=request.doctype,
        filters=filters,
        fields=fields,
        description=request.prompt,
        limit=50
    )
    
    return result


@router.get("/run/{tool_name}")
async def run_tool(tool_name: str):
    """Execute a saved tool and return results."""
    # Get tool config
    tool_result = await tool_registry.get_tool(tool_name)
    if tool_result["status"] != "success":
        return tool_result
    
    tool = tool_result["tool"]
    
    # Execute the query
    result = await erp_entity_service.query(
        doctype=tool["doctype"],
        filters=tool.get("filters"),
        fields=tool.get("fields"),
        limit=tool.get("limit", 50),
        order_by=tool.get("order_by", "creation desc")
    )
    
    # Track usage
    await tool_registry.increment_run_count(tool_name)
    
    if result["status"] == "success":
        return {
            "status": "success",
            "tool_name": tool_name,
            "doctype": tool["doctype"],
            "description": tool.get("description"),
            "data": result["data"],
            "count": result["count"],
            "fields": tool.get("fields", [])
        }
    return result


@router.delete("/{tool_name}")
async def delete_tool(tool_name: str):
    """Delete a saved tool."""
    return await tool_registry.delete_tool(tool_name)


def parse_prompt_to_filters(prompt: str, doctype: str) -> List:
    """Parse natural language prompt to ERPNext filters."""
    prompt_lower = prompt.lower()
    filters = []
    
    from datetime import datetime, timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Date filters
    if "today" in prompt_lower:
        if doctype in ["Sales Order", "Purchase Order"]:
            filters.append(["transaction_date", "=", today])
        elif doctype in ["Sales Invoice", "Purchase Invoice"]:
            filters.append(["posting_date", "=", today])
        else:
            filters.append(["creation", ">=", f"{today} 00:00:00"])
    
    elif "yesterday" in prompt_lower:
        if doctype in ["Sales Order", "Purchase Order"]:
            filters.append(["transaction_date", "=", yesterday])
        elif doctype in ["Sales Invoice", "Purchase Invoice"]:
            filters.append(["posting_date", "=", yesterday])
    
    elif "this week" in prompt_lower or "last 7 days" in prompt_lower:
        if doctype in ["Sales Order", "Purchase Order"]:
            filters.append(["transaction_date", ">=", week_ago])
        elif doctype in ["Sales Invoice", "Purchase Invoice"]:
            filters.append(["posting_date", ">=", week_ago])
        else:
            filters.append(["creation", ">=", f"{week_ago} 00:00:00"])
    
    elif "this month" in prompt_lower or "last 30 days" in prompt_lower:
        if doctype in ["Sales Order", "Purchase Order"]:
            filters.append(["transaction_date", ">=", month_ago])
        elif doctype in ["Sales Invoice", "Purchase Invoice"]:
            filters.append(["posting_date", ">=", month_ago])
    
    # Status filters
    if "pending" in prompt_lower or "draft" in prompt_lower:
        filters.append(["status", "=", "Draft"])
    elif "completed" in prompt_lower:
        filters.append(["status", "=", "Completed"])
    elif "cancelled" in prompt_lower:
        filters.append(["status", "=", "Cancelled"])
    elif "unpaid" in prompt_lower:
        filters.append(["status", "=", "Unpaid"])
    elif "paid" in prompt_lower:
        filters.append(["status", "=", "Paid"])
    elif "overdue" in prompt_lower:
        filters.append(["status", "=", "Overdue"])
    
    # Value filters
    if "high value" in prompt_lower or "large" in prompt_lower:
        filters.append(["grand_total", ">", 50000])
    elif "low value" in prompt_lower or "small" in prompt_lower:
        filters.append(["grand_total", "<", 10000])
    
    # Active/Disabled filters
    if "active" in prompt_lower:
        filters.append(["disabled", "=", 0])
    elif "disabled" in prompt_lower or "inactive" in prompt_lower:
        filters.append(["disabled", "=", 1])
    
    return filters


def get_default_fields(doctype: str) -> List[str]:
    """Get default fields for a DocType."""
    default_fields = {
        "Sales Order": ["name", "customer", "transaction_date", "grand_total", "status"],
        "Sales Invoice": ["name", "customer", "posting_date", "grand_total", "outstanding_amount", "status"],
        "Purchase Order": ["name", "supplier", "transaction_date", "grand_total", "status"],
        "Purchase Invoice": ["name", "supplier", "posting_date", "grand_total", "outstanding_amount", "status"],
        "Customer": ["name", "customer_name", "customer_type", "territory"],
        "Supplier": ["name", "supplier_name", "supplier_type"],
        "Item": ["name", "item_name", "item_group", "stock_uom"],
        "Company": ["name", "company_name", "default_currency", "country"],
        "Employee": ["name", "employee_name", "department", "designation", "status"],
        "Lead": ["name", "lead_name", "company_name", "status", "source"],
        "Opportunity": ["name", "party_name", "opportunity_type", "status", "opportunity_amount"],
    }
    return default_fields.get(doctype, ["name"])
