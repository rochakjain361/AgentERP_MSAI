"""ERPNext Service - Handles all ERPNext API interactions."""
import httpx
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from config import ERP_URL, ERP_API_KEY, ERP_API_SECRET, ERP_MOCK_MODE
from models import Customer, SalesOrder


class ERPNextService:
    """Service class for interacting with ERPNext API."""
    
    def __init__(self):
        self.base_url = ERP_URL
        self.api_key = ERP_API_KEY
        self.api_secret = ERP_API_SECRET
        self.mock_mode = ERP_MOCK_MODE
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_headers(self):
        return self.headers
    
    async def check_customer(self, customer_name: str) -> Dict[str, Any]:
        """Check if customer exists in ERPNext."""
        if self.mock_mode:
            await asyncio.sleep(0.5)
            existing_customers = ["ACME Corp", "TechCorp Inc", "Global Solutions"]
            if customer_name in existing_customers:
                return {
                    "status": "success",
                    "exists": True,
                    "data": {
                        "name": customer_name,
                        "customer_name": customer_name,
                        "customer_type": "Company",
                        "territory": "India"
                    }
                }
            return {"status": "success", "exists": False, "data": None}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Customer/{customer_name}"
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    customer_data = data.get("data", {})
                    return {
                        "status": "success",
                        "exists": True,
                        "data": {
                            "name": customer_data.get("name", customer_name),
                            "customer_name": customer_data.get("customer_name", customer_name),
                            "customer_type": customer_data.get("customer_type", "Company"),
                            "territory": customer_data.get("territory") or "Not Set"
                        }
                    }
                elif response.status_code == 404:
                    return {"status": "success", "exists": False, "data": None}
                else:
                    return {
                        "status": "error",
                        "message": f"ERPNext API error: {response.status_code} - {response.text}"
                    }
        except Exception as e:
            logging.error(f"Error checking customer: {str(e)}")
            return {"status": "error", "message": f"Failed to check customer: {str(e)}"}
    
    async def create_customer(self, customer: Customer) -> Dict[str, Any]:
        """Create a new customer in ERPNext."""
        if self.mock_mode:
            await asyncio.sleep(0.8)
            return {
                "status": "success",
                "message": f"Customer '{customer.customer_name}' created successfully",
                "data": {
                    "name": customer.customer_name,
                    "customer_type": customer.customer_type,
                    "territory": customer.territory,
                    "creation": datetime.now(timezone.utc).isoformat()
                }
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Customer"
                payload = {
                    "doctype": "Customer",
                    "customer_name": customer.customer_name,
                    "customer_type": customer.customer_type,
                    "territory": customer.territory
                }
                
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    customer_data = data.get("data", {})
                    return {
                        "status": "success",
                        "message": f"Customer '{customer.customer_name}' created successfully",
                        "data": {
                            "name": customer_data.get("name", customer.customer_name),
                            "customer_name": customer_data.get("customer_name", customer.customer_name),
                            "customer_type": customer_data.get("customer_type", customer.customer_type),
                            "territory": customer_data.get("territory", customer.territory),
                            "creation": customer_data.get("creation", datetime.now(timezone.utc).isoformat())
                        }
                    }
                else:
                    error_msg = response.json() if response.text else response.text
                    return {
                        "status": "error",
                        "message": f"Failed to create customer: {error_msg}"
                    }
        except Exception as e:
            logging.error(f"Error creating customer: {str(e)}")
            return {"status": "error", "message": f"Failed to create customer: {str(e)}"}
    
    async def create_sales_order(self, sales_order: SalesOrder, company: str = None) -> Dict[str, Any]:
        """Create a sales order in ERPNext."""
        if self.mock_mode:
            await asyncio.sleep(1.0)
            order_id = f"SO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            return {
                "status": "success",
                "message": f"Sales Order {order_id} created successfully",
                "data": {
                    "name": order_id,
                    "customer": sales_order.customer,
                    "transaction_date": sales_order.transaction_date,
                    "items": [item.model_dump() for item in sales_order.items],
                    "total_qty": sum(item.qty for item in sales_order.items),
                    "status": "Draft"
                }
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Sales Order"
                
                items_list = []
                for item in sales_order.items:
                    price_url = f"{self.base_url}/api/resource/Item Price"
                    price_params = {
                        "filters": json.dumps([["item_code", "=", item.item_code], ["price_list", "=", "Standard Selling"]]),
                        "fields": '["price_list_rate"]',
                        "limit_page_length": 1
                    }
                    
                    item_rate = 100.0
                    try:
                        price_response = await client.get(price_url, headers=self.headers, params=price_params)
                        if price_response.status_code == 200:
                            price_data = price_response.json().get("data", [])
                            if price_data and len(price_data) > 0:
                                item_rate = price_data[0].get("price_list_rate", 100.0)
                    except:
                        pass
                    
                    items_list.append({
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "rate": item_rate,
                        "delivery_date": sales_order.transaction_date,
                        "warehouse": "Finished Goods - IND"
                    })
                
                payload = {
                    "doctype": "Sales Order",
                    "naming_series": "SAL-ORD-",
                    "customer": sales_order.customer,
                    "transaction_date": sales_order.transaction_date,
                    "delivery_date": sales_order.transaction_date,
                    "currency": "INR",
                    "company": company or "India-Next (Demo)",
                    "selling_price_list": "Standard Selling",
                    "price_list_currency": "INR",
                    "plc_conversion_rate": 1.0,
                    "conversion_rate": 1.0,
                    "items": items_list
                }
                
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    order_data = data.get("data", {})
                    return {
                        "status": "success",
                        "message": f"Sales Order {order_data.get('name', 'created')} created successfully",
                        "data": {
                            "name": order_data.get("name"),
                            "customer": order_data.get("customer", sales_order.customer),
                            "transaction_date": order_data.get("transaction_date", sales_order.transaction_date),
                            "items": [{"item_code": item.item_code, "qty": item.qty} for item in sales_order.items],
                            "total_qty": sum(item.qty for item in sales_order.items),
                            "grand_total": order_data.get("grand_total", 0),
                            "status": order_data.get("status", "Draft")
                        }
                    }
                else:
                    error_data = response.json() if response.text else {}
                    error_msg = "Sales order creation failed"
                    
                    if isinstance(error_data, dict):
                        if 'exception' in error_data:
                            error_msg = error_data.get('exception', error_msg)
                        elif 'message' in error_data:
                            error_msg = error_data.get('message', error_msg)
                        elif '_server_messages' in error_data:
                            try:
                                messages = json.loads(error_data['_server_messages'])
                                if messages:
                                    first_msg = json.loads(messages[0])
                                    error_msg = first_msg.get('message', error_msg)
                            except:
                                pass
                    
                    return {
                        "status": "error",
                        "message": f"Unable to create sales order. {error_msg[:200]}"
                    }
        except Exception as e:
            logging.error(f"Error creating sales order: {str(e)}")
            return {"status": "error", "message": f"System error: {str(e)[:100]}"}
    
    async def get_sales_orders(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent sales orders."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Sales Order"
                params = {
                    "fields": '["name","customer","transaction_date","status","grand_total"]',
                    "limit_page_length": limit,
                    "order_by": "creation desc"
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get("data", [])
                    return {"status": "success", "data": orders}
                else:
                    return {"status": "error", "message": f"Failed to fetch sales orders: {response.status_code}"}
        except Exception as e:
            logging.error(f"Error getting sales orders: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_invoices(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent sales invoices."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Sales Invoice"
                params = {
                    "fields": '["name","customer","posting_date","status","grand_total","outstanding_amount"]',
                    "limit_page_length": limit,
                    "order_by": "creation desc"
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    invoices = data.get("data", [])
                    return {"status": "success", "data": invoices}
                else:
                    return {"status": "error", "message": f"Failed to fetch invoices: {response.status_code}"}
        except Exception as e:
            logging.error(f"Error getting invoices: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_customers(self, limit: int = 10) -> Dict[str, Any]:
        """Get all customers."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/api/resource/Customer"
                params = {
                    "fields": '["name","customer_name","customer_type","territory"]',
                    "limit_page_length": limit,
                    "order_by": "creation desc"
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    customers = data.get("data", [])
                    return {"status": "success", "data": customers}
                else:
                    return {"status": "error", "message": f"Failed to fetch customers: {response.status_code}"}
        except Exception as e:
            logging.error(f"Error getting customers: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get ERP dashboard statistics."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                stats = {}
                
                customer_response = await client.get(
                    f"{self.base_url}/api/resource/Customer?limit_page_length=1",
                    headers=self.headers
                )
                if customer_response.status_code == 200:
                    stats['total_customers'] = customer_response.json().get('count', 0) or len(customer_response.json().get('data', []))
                
                so_response = await client.get(
                    f"{self.base_url}/api/resource/Sales Order?limit_page_length=1",
                    headers=self.headers
                )
                if so_response.status_code == 200:
                    stats['total_sales_orders'] = so_response.json().get('count', 0) or len(so_response.json().get('data', []))
                
                inv_response = await client.get(
                    f"{self.base_url}/api/resource/Sales Invoice?limit_page_length=1",
                    headers=self.headers
                )
                if inv_response.status_code == 200:
                    stats['total_invoices'] = inv_response.json().get('count', 0) or len(inv_response.json().get('data', []))
                
                item_response = await client.get(
                    f"{self.base_url}/api/resource/Item?limit_page_length=1",
                    headers=self.headers
                )
                if item_response.status_code == 200:
                    stats['total_items'] = item_response.json().get('count', 0) or len(item_response.json().get('data', []))
                
                return {"status": "success", "data": stats}
        except Exception as e:
            logging.error(f"Error getting dashboard stats: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive ERP analytics with detailed breakdowns."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                analytics = {
                    "summary": {},
                    "top_customers": [],
                    "recent_orders": [],
                    "recent_invoices": [],
                    "sales_by_status": {},
                    "outstanding_receivables": 0,
                    "top_items": [],
                    "monthly_trends": []
                }
                
                # Get detailed sales orders
                so_response = await client.get(
                    f"{self.base_url}/api/resource/Sales Order",
                    headers=self.headers,
                    params={
                        "fields": '["name","customer","transaction_date","status","grand_total","total_qty"]',
                        "limit_page_length": 100,
                        "order_by": "creation desc"
                    }
                )
                
                if so_response.status_code == 200:
                    orders = so_response.json().get("data", [])
                    analytics["recent_orders"] = orders[:10]
                    
                    total_sales = sum(float(o.get("grand_total", 0) or 0) for o in orders)
                    analytics["summary"]["total_sales_value"] = round(total_sales, 2)
                    analytics["summary"]["total_orders"] = len(orders)
                    analytics["summary"]["avg_order_value"] = round(total_sales / len(orders), 2) if orders else 0
                    
                    status_counts = {}
                    for order in orders:
                        status = order.get("status", "Unknown")
                        if status not in status_counts:
                            status_counts[status] = {"count": 0, "value": 0}
                        status_counts[status]["count"] += 1
                        status_counts[status]["value"] += float(order.get("grand_total", 0) or 0)
                    analytics["sales_by_status"] = status_counts
                    
                    customer_totals = {}
                    for order in orders:
                        customer = order.get("customer", "Unknown")
                        if customer not in customer_totals:
                            customer_totals[customer] = {"order_count": 0, "total_value": 0}
                        customer_totals[customer]["order_count"] += 1
                        customer_totals[customer]["total_value"] += float(order.get("grand_total", 0) or 0)
                    
                    sorted_customers = sorted(
                        customer_totals.items(),
                        key=lambda x: x[1]["total_value"],
                        reverse=True
                    )[:5]
                    analytics["top_customers"] = [
                        {"customer": k, "order_count": v["order_count"], "total_value": round(v["total_value"], 2)}
                        for k, v in sorted_customers
                    ]
                
                # Get invoices
                inv_response = await client.get(
                    f"{self.base_url}/api/resource/Sales Invoice",
                    headers=self.headers,
                    params={
                        "fields": '["name","customer","posting_date","status","grand_total","outstanding_amount"]',
                        "limit_page_length": 50,
                        "order_by": "creation desc"
                    }
                )
                
                if inv_response.status_code == 200:
                    invoices = inv_response.json().get("data", [])
                    analytics["recent_invoices"] = invoices[:10]
                    analytics["summary"]["total_invoices"] = len(invoices)
                    
                    outstanding = sum(float(inv.get("outstanding_amount", 0) or 0) for inv in invoices)
                    analytics["outstanding_receivables"] = round(outstanding, 2)
                    analytics["summary"]["total_invoiced"] = round(
                        sum(float(inv.get("grand_total", 0) or 0) for inv in invoices), 2
                    )
                
                # Get customer count
                cust_response = await client.get(
                    f"{self.base_url}/api/resource/Customer",
                    headers=self.headers,
                    params={"limit_page_length": 500, "fields": '["name"]'}
                )
                if cust_response.status_code == 200:
                    analytics["summary"]["total_customers"] = len(cust_response.json().get("data", []))
                
                # Get items
                item_response = await client.get(
                    f"{self.base_url}/api/resource/Item",
                    headers=self.headers,
                    params={
                        "fields": '["name","item_name","item_group","stock_uom"]',
                        "limit_page_length": 100
                    }
                )
                if item_response.status_code == 200:
                    items = item_response.json().get("data", [])
                    analytics["summary"]["total_items"] = len(items)
                    analytics["top_items"] = items[:10]
                
                return {"status": "success", "data": analytics}
        except Exception as e:
            logging.error(f"Error getting comprehensive analytics: {str(e)}")
            return {"status": "error", "message": str(e)}


# Singleton instance
erp_service = ERPNextService()
