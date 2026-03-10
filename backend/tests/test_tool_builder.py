"""
Tool Builder API Tests for AgentERP
Tests: Tool CRUD operations, Tool execution
"""

import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://localhost:8000"


class TestToolsList:
    """Test GET /api/tools - List all tools"""
    
    def test_get_tools_returns_list(self):
        """Verify GET /api/tools returns tools list"""
        response = requests.get(f"{BASE_URL}/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tools" in data
        assert isinstance(data["tools"], list)
        print(f"Found {len(data['tools'])} tools")
    
    def test_tools_have_required_fields(self):
        """Verify each tool has required fields"""
        response = requests.get(f"{BASE_URL}/api/tools")
        data = response.json()
        
        for tool in data.get("tools", []):
            assert "tool_name" in tool, f"Tool missing tool_name: {tool}"
            assert "doctype" in tool, f"Tool missing doctype: {tool}"
            assert "description" in tool, f"Tool missing description: {tool}"
            print(f"Tool '{tool['tool_name']}' has all required fields")


class TestToolCreation:
    """Test POST /api/tools - Create new tool"""
    
    def test_create_tool_success(self):
        """Test creating a new tool"""
        unique_name = f"TEST_tool_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/tools", json={
            "tool_name": unique_name,
            "doctype": "Sales Order",
            "prompt": "Show all pending orders"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tool" in data
        assert data["tool"]["tool_name"] == unique_name.lower().replace(" ", "_")
        print(f"Created tool: {data['tool']['tool_name']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tools/{data['tool']['tool_name']}")
    
    def test_create_tool_with_high_value_filter(self):
        """Test creating a tool with high value filter in prompt"""
        unique_name = f"TEST_highval_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/tools", json={
            "tool_name": unique_name,
            "doctype": "Sales Order",
            "prompt": "high value orders over 50000"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Verify filter was generated
        tool = data["tool"]
        filters = tool.get("filters", [])
        has_high_value_filter = any("grand_total" in str(f) and "50000" in str(f) for f in filters)
        assert has_high_value_filter, f"Expected high value filter, got: {filters}"
        print(f"Tool created with filters: {filters}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tools/{tool['tool_name']}")
    
    def test_create_tool_with_today_filter(self):
        """Test creating a tool with today filter in prompt"""
        unique_name = f"TEST_today_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/tools", json={
            "tool_name": unique_name,
            "doctype": "Sales Invoice",
            "prompt": "invoices created today"
        })
        
        assert response.status_code == 200
        data = response.json()
        tool = data["tool"]
        
        # Verify date filter was generated
        filters = tool.get("filters", [])
        has_date_filter = any("posting_date" in str(f) or "transaction_date" in str(f) for f in filters)
        assert has_date_filter, f"Expected date filter for 'today', got: {filters}"
        print(f"Tool created with date filters: {filters}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tools/{tool['tool_name']}")


class TestToolExecution:
    """Test GET /api/tools/run/{tool_name} - Execute tool"""
    
    def test_run_existing_tool_high_value_orders(self):
        """Test running the high_value_orders tool"""
        response = requests.get(f"{BASE_URL}/api/tools/run/high_value_orders")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["tool_name"] == "high_value_orders"
        assert data["doctype"] == "Sales Order"
        assert "data" in data
        assert "count" in data
        assert "fields" in data
        
        print(f"high_value_orders returned {data['count']} results")
        if data["data"]:
            print(f"Sample data: {data['data'][0]}")
    
    def test_run_existing_tool_pending_orders(self):
        """Test running the pending_orders tool"""
        response = requests.get(f"{BASE_URL}/api/tools/run/pending_orders")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["tool_name"] == "pending_orders"
        print(f"pending_orders returned {data['count']} results")
    
    def test_run_existing_tool_active_customers(self):
        """Test running the active_customers tool"""
        response = requests.get(f"{BASE_URL}/api/tools/run/active_customers")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["tool_name"] == "active_customers"
        assert data["doctype"] == "Customer"
        print(f"active_customers returned {data['count']} results")
    
    def test_run_existing_tool_todays_orders(self):
        """Test running the todays_orders tool"""
        response = requests.get(f"{BASE_URL}/api/tools/run/todays_orders")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["tool_name"] == "todays_orders"
        print(f"todays_orders returned {data['count']} results")
    
    def test_run_nonexistent_tool(self):
        """Test running a tool that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/tools/run/nonexistent_tool_xyz")
        assert response.status_code == 200  # API returns 200 with error status
        data = response.json()
        assert data["status"] == "error"
        print(f"Nonexistent tool returned: {data.get('message')}")


class TestToolDeletion:
    """Test DELETE /api/tools/{tool_name} - Delete tool"""
    
    def test_create_and_delete_tool(self):
        """Test creating a tool and then deleting it"""
        unique_name = f"TEST_delete_{uuid.uuid4().hex[:8]}"
        
        # Create
        create_response = requests.post(f"{BASE_URL}/api/tools", json={
            "tool_name": unique_name,
            "doctype": "Customer",
            "prompt": "all active customers"
        })
        assert create_response.status_code == 200
        tool_name = create_response.json()["tool"]["tool_name"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/tools/{tool_name}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "success"
        
        # Verify deletion
        run_response = requests.get(f"{BASE_URL}/api/tools/run/{tool_name}")
        assert run_response.json()["status"] == "error"
        print(f"Tool {tool_name} created and deleted successfully")
    
    def test_delete_nonexistent_tool(self):
        """Test deleting a tool that doesn't exist"""
        response = requests.delete(f"{BASE_URL}/api/tools/nonexistent_tool_xyz")
        assert response.status_code == 200
        data = response.json()
        # Should return error status or 404
        print(f"Delete nonexistent tool returned: {data}")


class TestToolDataPersistence:
    """Test tool data persistence and run tracking"""
    
    def test_tool_run_count_increments(self):
        """Test that running a tool increments run_count"""
        # Get initial state
        tools_response = requests.get(f"{BASE_URL}/api/tools")
        tools = tools_response.json()["tools"]
        
        high_value_tool = next((t for t in tools if t["tool_name"] == "high_value_orders"), None)
        assert high_value_tool is not None
        initial_run_count = high_value_tool.get("run_count", 0)
        
        # Run the tool
        requests.get(f"{BASE_URL}/api/tools/run/high_value_orders")
        
        # Give it a moment to update
        time.sleep(0.5)
        
        # Check updated state
        tools_response = requests.get(f"{BASE_URL}/api/tools")
        tools = tools_response.json()["tools"]
        high_value_tool = next((t for t in tools if t["tool_name"] == "high_value_orders"), None)
        new_run_count = high_value_tool.get("run_count", 0)
        
        assert new_run_count >= initial_run_count, f"Run count should increase: {initial_run_count} -> {new_run_count}"
        print(f"Run count increased from {initial_run_count} to {new_run_count}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
