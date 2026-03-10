"""Entity routes - Generic CRUD operations for any ERPNext DocType."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from services.erp_entity_service import erp_entity_service
from services.tool_registry import tool_registry

router = APIRouter(prefix="/entity", tags=["entity"])


# Request Models
class EntityRequest(BaseModel):
    """Generic entity request model."""
    action: str = Field(..., description="Action: create, read, update, delete, query")
    doctype: str = Field(..., description="ERPNext DocType name")
    name: Optional[str] = Field(None, description="Entity name (for read/update/delete)")
    data: Optional[Dict[str, Any]] = Field(None, description="Entity data (for create/update)")
    filters: Optional[List] = Field(None, description="Query filters")
    fields: Optional[List[str]] = Field(None, description="Fields to return")
    limit: Optional[int] = Field(20, description="Query limit")
    order_by: Optional[str] = Field("creation desc", description="Order by clause")
    skip_validation: Optional[bool] = Field(False, description="Skip validation on create")


class ToolRequest(BaseModel):
    """Tool management request model."""
    action: str = Field(..., description="Action: create_tool, run_tool, list_tools, get_tool, update_tool, delete_tool")
    tool_name: Optional[str] = Field(None, description="Tool name")
    doctype: Optional[str] = Field(None, description="DocType for the tool")
    filters: Optional[List] = Field(None, description="Query filters")
    fields: Optional[List[str]] = Field(None, description="Fields to return")
    description: Optional[str] = Field(None, description="Tool description")
    limit: Optional[int] = Field(20, description="Query limit")
    order_by: Optional[str] = Field("creation desc", description="Order by clause")
    updates: Optional[Dict[str, Any]] = Field(None, description="Updates for update_tool")


class InteractiveCreateRequest(BaseModel):
    """Interactive creation request."""
    doctype: str
    data: Dict[str, Any]
    session_id: Optional[str] = None


# Entity CRUD Endpoints
@router.post("")
async def entity_operation(request: EntityRequest):
    """
    Generic entity operation endpoint.
    
    Supports: create, read, update, delete, query
    
    Examples:
    - Create: {"action": "create", "doctype": "Customer", "data": {"customer_name": "ACME"}}
    - Read: {"action": "read", "doctype": "Customer", "name": "ACME Corp"}
    - Update: {"action": "update", "doctype": "Customer", "name": "ACME Corp", "data": {"territory": "USA"}}
    - Delete: {"action": "delete", "doctype": "Customer", "name": "ACME Corp"}
    - Query: {"action": "query", "doctype": "Sales Order", "filters": [["customer","=","ACME Corp"]], "fields": ["name","grand_total"]}
    """
    action = request.action.lower()
    
    if action == "create":
        if not request.data:
            return {"status": "error", "message": "Data is required for create action"}
        return await erp_entity_service.create(
            request.doctype, 
            request.data, 
            skip_validation=request.skip_validation
        )
    
    elif action == "read":
        if not request.name:
            return {"status": "error", "message": "Name is required for read action"}
        return await erp_entity_service.read(request.doctype, request.name, request.fields)
    
    elif action == "update":
        if not request.name or not request.data:
            return {"status": "error", "message": "Name and data are required for update action"}
        return await erp_entity_service.update(request.doctype, request.name, request.data)
    
    elif action == "delete":
        if not request.name:
            return {"status": "error", "message": "Name is required for delete action"}
        return await erp_entity_service.delete(request.doctype, request.name)
    
    elif action == "query":
        return await erp_entity_service.query(
            request.doctype,
            filters=request.filters,
            fields=request.fields,
            limit=request.limit,
            order_by=request.order_by
        )
    
    elif action == "meta":
        return await erp_entity_service.get_doctype_meta(request.doctype)
    
    elif action == "validate":
        if not request.data:
            return {"status": "error", "message": "Data is required for validate action"}
        return await erp_entity_service.validate_entity(request.doctype, request.data)
    
    elif action == "exists":
        if not request.name:
            return {"status": "error", "message": "Name is required for exists action"}
        exists = await erp_entity_service.entity_exists(request.doctype, request.name)
        return {"status": "success", "exists": exists, "doctype": request.doctype, "name": request.name}
    
    else:
        return {
            "status": "error",
            "message": f"Unknown action: {action}",
            "supported_actions": ["create", "read", "update", "delete", "query", "meta", "validate", "exists"]
        }


@router.post("/interactive-create")
async def interactive_create(request: InteractiveCreateRequest):
    """
    Interactive entity creation with guided field collection.
    
    If required fields are missing, returns the missing fields list
    so the frontend can ask the user for them.
    """
    # First, validate the entity
    validation = await erp_entity_service.validate_entity(request.doctype, request.data)
    
    if validation["status"] == "missing_fields":
        # Get metadata to provide field info
        meta = await erp_entity_service.get_doctype_meta(request.doctype)
        field_info = {}
        
        if meta["status"] == "success":
            all_fields = {f["name"]: f for f in meta.get("fields", [])}
            for field_name in validation["missing_fields"]:
                if field_name in all_fields:
                    field_info[field_name] = all_fields[field_name]
        
        return {
            "status": "needs_input",
            "message": f"Please provide the following fields for {request.doctype}",
            "missing_fields": validation["missing_fields"],
            "field_info": field_info,
            "current_data": request.data
        }
    
    elif validation["status"] == "invalid_references":
        return {
            "status": "invalid_references",
            "message": validation["message"],
            "invalid_references": validation["invalid_references"],
            "suggestions": "Please verify the referenced entities exist in ERPNext"
        }
    
    # Validation passed, create the entity
    return await erp_entity_service.create(request.doctype, request.data, skip_validation=True)


# Tool Registry Endpoints
@router.post("/tool")
async def tool_operation(request: ToolRequest):
    """
    Tool registry operations.
    
    Supports: create_tool, run_tool, list_tools, get_tool, update_tool, delete_tool
    
    Examples:
    - Create: {"action": "create_tool", "tool_name": "high_value_orders", "doctype": "Sales Order", "filters": [["grand_total",">",100000]]}
    - Run: {"action": "run_tool", "tool_name": "high_value_orders"}
    - List: {"action": "list_tools"}
    """
    action = request.action.lower()
    
    if action == "create_tool":
        if not request.tool_name or not request.doctype:
            return {"status": "error", "message": "tool_name and doctype are required"}
        return await tool_registry.create_tool(
            tool_name=request.tool_name,
            doctype=request.doctype,
            filters=request.filters,
            fields=request.fields,
            description=request.description,
            limit=request.limit,
            order_by=request.order_by
        )
    
    elif action == "run_tool":
        if not request.tool_name:
            return {"status": "error", "message": "tool_name is required"}
        
        # Get tool config
        tool_result = await tool_registry.get_tool(request.tool_name)
        if tool_result["status"] != "success":
            return tool_result
        
        tool = tool_result["tool"]
        
        # Execute the query
        result = await erp_entity_service.query(
            doctype=tool["doctype"],
            filters=tool.get("filters"),
            fields=tool.get("fields"),
            limit=tool.get("limit", 20),
            order_by=tool.get("order_by", "creation desc")
        )
        
        # Track usage
        await tool_registry.increment_run_count(request.tool_name)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "tool_name": request.tool_name,
                "description": tool.get("description"),
                "doctype": tool["doctype"],
                "data": result["data"],
                "count": result["count"]
            }
        return result
    
    elif action == "list_tools":
        return await tool_registry.list_tools()
    
    elif action == "get_tool":
        if not request.tool_name:
            return {"status": "error", "message": "tool_name is required"}
        return await tool_registry.get_tool(request.tool_name)
    
    elif action == "update_tool":
        if not request.tool_name:
            return {"status": "error", "message": "tool_name is required"}
        updates = request.updates or {}
        if request.filters is not None:
            updates["filters"] = request.filters
        if request.fields is not None:
            updates["fields"] = request.fields
        if request.description is not None:
            updates["description"] = request.description
        if request.limit is not None:
            updates["limit"] = request.limit
        if request.order_by is not None:
            updates["order_by"] = request.order_by
        return await tool_registry.update_tool(request.tool_name, updates)
    
    elif action == "delete_tool":
        if not request.tool_name:
            return {"status": "error", "message": "tool_name is required"}
        return await tool_registry.delete_tool(request.tool_name)
    
    else:
        return {
            "status": "error",
            "message": f"Unknown action: {action}",
            "supported_actions": ["create_tool", "run_tool", "list_tools", "get_tool", "update_tool", "delete_tool"]
        }


# Convenience endpoints
@router.get("/doctypes")
async def list_common_doctypes():
    """List commonly used ERPNext DocTypes."""
    return {
        "status": "success",
        "doctypes": [
            {"name": "Customer", "module": "Selling"},
            {"name": "Supplier", "module": "Buying"},
            {"name": "Item", "module": "Stock"},
            {"name": "Sales Order", "module": "Selling"},
            {"name": "Sales Invoice", "module": "Accounts"},
            {"name": "Purchase Order", "module": "Buying"},
            {"name": "Purchase Invoice", "module": "Accounts"},
            {"name": "Stock Entry", "module": "Stock"},
            {"name": "Journal Entry", "module": "Accounts"},
            {"name": "Payment Entry", "module": "Accounts"},
            {"name": "Warehouse", "module": "Stock"},
            {"name": "Company", "module": "Setup"},
            {"name": "Employee", "module": "HR"},
            {"name": "Lead", "module": "CRM"},
            {"name": "Opportunity", "module": "CRM"},
        ]
    }


@router.get("/meta/{doctype}")
async def get_doctype_metadata(doctype: str):
    """Get metadata for a specific DocType."""
    return await erp_entity_service.get_doctype_meta(doctype)
