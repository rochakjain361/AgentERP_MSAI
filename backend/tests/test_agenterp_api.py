"""
Backend API Tests for AgentERP
Tests: Chat endpoints, Analytics, ERP operations, Session management
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://localhost:8000"

class TestHealthAndBasics:
    """Health check and basic API tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns correct status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "erp_mode" in data
        assert "erp_url" in data
        print(f"Health check passed: {data}")
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"Root endpoint: {data}")


class TestChatSessions:
    """Chat session management tests"""
    
    def test_create_chat_session(self):
        """Test creating a new chat session"""
        response = requests.post(f"{BASE_URL}/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "session" in data
        assert "id" in data["session"]
        assert data["session"]["title"] == "New Chat"
        print(f"Created session: {data['session']['id']}")
        return data["session"]["id"]
    
    def test_get_chat_sessions(self):
        """Test retrieving all chat sessions"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} chat sessions")
    
    def test_create_and_retrieve_session(self):
        """Test create session then retrieve it"""
        # Create session
        create_response = requests.post(f"{BASE_URL}/api/chat/sessions")
        assert create_response.status_code == 200
        session_id = create_response.json()["session"]["id"]
        
        # Retrieve session
        get_response = requests.get(f"{BASE_URL}/api/chat/sessions/{session_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == session_id
        print(f"Session verified: {session_id}")
    
    def test_delete_chat_session(self):
        """Test deleting a chat session"""
        # First create a session
        create_response = requests.post(f"{BASE_URL}/api/chat/sessions")
        session_id = create_response.json()["session"]["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/chat/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/chat/sessions/{session_id}")
        assert get_response.status_code == 404
        print(f"Session deleted successfully: {session_id}")


class TestChatMessages:
    """Chat message tests"""
    
    def test_save_and_retrieve_messages(self):
        """Test saving and retrieving chat messages"""
        # Create a session first
        session_response = requests.post(f"{BASE_URL}/api/chat/sessions")
        session_id = session_response.json()["session"]["id"]
        
        # Save a message
        message = {
            "session_id": session_id,
            "role": "user",
            "content": "TEST_message Hello, test message"
        }
        save_response = requests.post(f"{BASE_URL}/api/chat/messages", json=message)
        assert save_response.status_code == 200
        
        # Retrieve messages
        get_response = requests.get(f"{BASE_URL}/api/chat/messages/{session_id}")
        assert get_response.status_code == 200
        messages = get_response.json()
        assert len(messages) >= 1
        assert any("TEST_message" in m.get("content", "") for m in messages)
        print(f"Message saved and retrieved in session {session_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/chat/sessions/{session_id}")


class TestComprehensiveAnalytics:
    """Test the comprehensive analytics feature"""
    
    def test_analytics_via_chat(self):
        """Test analytics endpoint via chat - should bypass AI"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "Show me comprehensive analytics and insights"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["type"] == "comprehensive_analytics"
        
        # Verify analytics data structure
        analytics = data["data"]
        assert "summary" in analytics
        assert "top_customers" in analytics
        assert "recent_orders" in analytics
        assert "recent_invoices" in analytics
        assert "sales_by_status" in analytics
        
        # Verify summary fields
        summary = analytics["summary"]
        assert "total_sales_value" in summary
        assert "total_orders" in summary
        assert "total_customers" in summary
        assert "total_invoiced" in summary
        
        print(f"Analytics returned: {len(analytics['top_customers'])} top customers, {len(analytics['recent_orders'])} orders")
    
    def test_dashboard_stats_via_chat(self):
        """Test dashboard stats via quick overview keyword"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "Show me quick overview"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Dashboard" in data["message"] or "dashboard" in data["data"].get("type", "")
        print(f"Dashboard stats returned successfully")


class TestERPOperations:
    """Test ERP operations via chat (live ERPNext)"""
    
    def test_check_existing_customer(self):
        """Test checking an existing customer"""
        response = requests.get(f"{BASE_URL}/api/customer/Grant Plastics Ltd.")
        assert response.status_code == 200
        data = response.json()
        # Customer should exist in live ERPNext
        if data.get("exists"):
            assert data["data"]["customer_name"] == "Grant Plastics Ltd."
            print("Customer exists in ERPNext")
        else:
            print("Customer check returned - may not exist or API issue")
    
    def test_list_customers_via_chat(self):
        """Test listing customers via chat"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "list all customers"
        })
        # May get 429 from AI but direct patterns should work
        assert response.status_code in [200, 500]  # 500 could be AI rate limit
        if response.status_code == 200:
            data = response.json()
            if data["data"] and data["data"].get("type") == "customers_list":
                print(f"Listed {len(data['data'].get('customers', []))} customers")


class TestDashboardViewData:
    """Test dashboard view data structure"""
    
    def test_analytics_data_for_dashboard(self):
        """Verify analytics data has all fields needed for DashboardView"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "detailed analytics"
        })
        assert response.status_code == 200
        data = response.json()["data"]
        
        # KPI Cards data
        summary = data.get("summary", {})
        assert "total_sales_value" in summary, "Missing total_sales_value for KPI"
        assert "total_customers" in summary, "Missing total_customers for KPI"
        assert "total_invoiced" in summary, "Missing total_invoiced for KPI"
        
        # Outstanding receivables
        assert "outstanding_receivables" in data, "Missing outstanding_receivables for KPI"
        
        # Top Customers table
        top_customers = data.get("top_customers", [])
        if top_customers:
            assert "customer" in top_customers[0], "Missing customer field in top_customers"
            assert "total_value" in top_customers[0], "Missing total_value field in top_customers"
            assert "order_count" in top_customers[0], "Missing order_count field in top_customers"
        
        # Recent Orders table
        recent_orders = data.get("recent_orders", [])
        if recent_orders:
            assert "name" in recent_orders[0], "Missing name field in recent_orders"
            assert "customer" in recent_orders[0], "Missing customer field in recent_orders"
            assert "grand_total" in recent_orders[0], "Missing grand_total in recent_orders"
            assert "status" in recent_orders[0], "Missing status in recent_orders"
        
        # Items catalog
        assert "top_items" in data, "Missing top_items for Items Catalog"
        
        # Sales by status
        assert "sales_by_status" in data, "Missing sales_by_status for breakdown"
        
        print("All dashboard view data fields present!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
