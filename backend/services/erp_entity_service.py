"""Generic ERP Entity Service - CRUD operations for any ERPNext DocType."""
import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from config import ERP_URL, ERP_API_KEY, ERP_API_SECRET


# Required fields for common DocTypes (for validation)
REQUIRED_FIELDS = {
    "Sales Order": ["customer", "items"],
    "Sales Invoice": ["customer", "items"],
    "Purchase Order": ["supplier", "items"],
    "Customer": ["customer_name"],
    "Supplier": ["supplier_name"],
    "Item": ["item_code", "item_name"],
    "Company": ["company_name", "default_currency"],
}

# Related entity validations
ENTITY_VALIDATIONS = {
    "Sales Order": {
        "customer": {"doctype": "Customer", "field": "name"},
        "items.item_code": {"doctype": "Item", "field": "name"},
        "items.warehouse": {"doctype": "Warehouse", "field": "name"},
    },
    "Sales Invoice": {
        "customer": {"doctype": "Customer", "field": "name"},
        "items.item_code": {"doctype": "Item", "field": "name"},
    },
    "Purchase Order": {
        "supplier": {"doctype": "Supplier", "field": "name"},
        "items.item_code": {"doctype": "Item", "field": "name"},
    },
}


class ERPEntityService:
    """Generic service for CRUD operations on any ERPNext DocType."""
    
    def __init__(self):
        self.base_url = ERP_URL
        self.headers = {
            "Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(self, method: str, url: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to ERPNext API."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    return {"status": "error", "message": f"Unknown method: {method}"}
                
                if response.status_code in [200, 201]:
                    return {"status": "success", "data": response.json()}
                elif response.status_code == 404:
                    return {"status": "error", "message": "Resource not found", "code": 404}
                else:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        if "_server_messages" in error_data:
                            messages = json.loads(error_data["_server_messages"])
                            if messages:
                                error_msg = json.loads(messages[0]).get("message", error_msg)
                        elif "message" in error_data:
                            error_msg = error_data["message"]
                    except:
                        pass
                    return {"status": "error", "message": error_msg, "code": response.status_code}
        except Exception as e:
            logging.error(f"ERPNext API error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def entity_exists(self, doctype: str, name: str) -> bool:
        """Check if an entity exists in ERPNext."""
        url = f"{self.base_url}/api/resource/{doctype}/{name}"
        result = await self._make_request("GET", url)
        return result["status"] == "success"
    
    async def validate_entity(self, doctype: str, data: Dict) -> Dict[str, Any]:
        """Validate entity data before creation."""
        missing_fields = []
        invalid_references = []
        
        # Check required fields
        required = REQUIRED_FIELDS.get(doctype, [])
        for field in required:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "status": "missing_fields",
                "missing_fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Validate related entities
        validations = ENTITY_VALIDATIONS.get(doctype, {})
        for field_path, validation in validations.items():
            if "." in field_path:
                # Handle nested fields (e.g., items.item_code)
                parent, child = field_path.split(".")
                if parent in data and isinstance(data[parent], list):
                    for idx, item in enumerate(data[parent]):
                        if child in item:
                            exists = await self.entity_exists(validation["doctype"], item[child])
                            if not exists:
                                invalid_references.append({
                                    "field": f"{parent}[{idx}].{child}",
                                    "value": item[child],
                                    "expected_doctype": validation["doctype"]
                                })
            else:
                # Handle simple fields
                if field_path in data:
                    exists = await self.entity_exists(validation["doctype"], data[field_path])
                    if not exists:
                        invalid_references.append({
                            "field": field_path,
                            "value": data[field_path],
                            "expected_doctype": validation["doctype"]
                        })
        
        if invalid_references:
            error_msgs = [f"{ref['field']}='{ref['value']}' ({ref['expected_doctype']} not found)" 
                         for ref in invalid_references]
            return {
                "status": "invalid_references",
                "invalid_references": invalid_references,
                "message": f"Invalid references: {'; '.join(error_msgs)}"
            }
        
        return {"status": "valid"}
    
    async def create(self, doctype: str, data: Dict, skip_validation: bool = False) -> Dict[str, Any]:
        """Create a new entity in ERPNext."""
        # Validate first
        if not skip_validation:
            validation = await self.validate_entity(doctype, data)
            if validation["status"] != "valid":
                return validation
        
        # Add doctype to data
        data["doctype"] = doctype
        
        url = f"{self.base_url}/api/resource/{doctype}"
        result = await self._make_request("POST", url, data=data)
        
        if result["status"] == "success":
            entity_data = result["data"].get("data", {})
            return {
                "status": "success",
                "message": f"{doctype} '{entity_data.get('name', 'unknown')}' created successfully",
                "data": entity_data
            }
        return result
    
    async def read(self, doctype: str, name: str, fields: List[str] = None) -> Dict[str, Any]:
        """Read a single entity from ERPNext."""
        url = f"{self.base_url}/api/resource/{doctype}/{name}"
        params = {}
        if fields:
            params["fields"] = json.dumps(fields)
        
        result = await self._make_request("GET", url, params=params)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "data": result["data"].get("data", {})
            }
        return result
    
    async def update(self, doctype: str, name: str, data: Dict) -> Dict[str, Any]:
        """Update an existing entity in ERPNext."""
        url = f"{self.base_url}/api/resource/{doctype}/{name}"
        result = await self._make_request("PUT", url, data=data)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"{doctype} '{name}' updated successfully",
                "data": result["data"].get("data", {})
            }
        return result
    
    async def delete(self, doctype: str, name: str) -> Dict[str, Any]:
        """Delete an entity from ERPNext."""
        url = f"{self.base_url}/api/resource/{doctype}/{name}"
        result = await self._make_request("DELETE", url)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"{doctype} '{name}' deleted successfully"
            }
        return result
    
    async def query(self, doctype: str, filters: List = None, fields: List[str] = None, 
                    limit: int = 20, order_by: str = "creation desc",
                    company_filter: str = None) -> Dict[str, Any]:
        """Query entities from ERPNext with filters and optional company filtering."""
        url = f"{self.base_url}/api/resource/{doctype}"
        params = {
            "limit_page_length": limit,
            "order_by": order_by
        }
        
        # Build filters list
        query_filters = filters.copy() if filters else []
        
        # Add company filter for non-admin users
        if company_filter:
            # Different DocTypes have different company fields
            company_field_map = {
                "Sales Order": "customer",
                "Sales Invoice": "customer",
                "Quotation": "party_name",
                "Delivery Note": "customer",
                "Customer": "name",  # Filter customers by name match
            }
            
            field = company_field_map.get(doctype, "customer")
            
            if doctype == "Customer":
                # For customer, filter by name containing company
                query_filters.append([field, "like", f"%{company_filter}%"])
            else:
                # For orders/invoices, filter by customer
                query_filters.append([field, "=", company_filter])
        
        if query_filters:
            params["filters"] = json.dumps(query_filters)
        if fields:
            params["fields"] = json.dumps(fields)
        
        result = await self._make_request("GET", url, params=params)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "data": result["data"].get("data", []),
                "count": len(result["data"].get("data", []))
            }
        return result
    
    async def get_doctype_meta(self, doctype: str) -> Dict[str, Any]:
        """Get metadata about a DocType (fields, required fields, etc.)."""
        url = f"{self.base_url}/api/resource/DocType/{doctype}"
        params = {"fields": '["fields"]'}
        
        result = await self._make_request("GET", url, params=params)
        
        if result["status"] == "success":
            doc_data = result["data"].get("data", {})
            fields = doc_data.get("fields", [])
            
            required_fields = [f["fieldname"] for f in fields if f.get("reqd")]
            all_fields = [{"name": f["fieldname"], "type": f.get("fieldtype"), "label": f.get("label")} 
                         for f in fields if f.get("fieldname")]
            
            return {
                "status": "success",
                "doctype": doctype,
                "required_fields": required_fields,
                "fields": all_fields
            }
        return result


# Singleton instance
erp_entity_service = ERPEntityService()
