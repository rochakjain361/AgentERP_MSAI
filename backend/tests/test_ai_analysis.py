"""
Test AI Analysis API - RBAC and Risk Classification

Tests:
1. /api/ai-analysis/access-check - Returns has_access:true for Admin/Manager, false for Operator/Viewer
2. /api/ai-analysis/analyze - Returns 403 for Operator/Viewer, 200 for Admin/Manager
3. /api/ai-analysis/execute - Returns 403 for Operator/Viewer, 200 for Admin/Manager
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CREDENTIALS = {
    "admin": {"email": "admin@agenterp.com", "password": "admin123"},
    "manager": {"email": "manager@techcorp.com", "password": "manager123"},
    "operator": {"email": "operator@innovate.com", "password": "operator123"},
    "viewer": {"email": "viewer@global.com", "password": "viewer123"},
}


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def get_auth_token(api_client, role):
    """Get authentication token for a specific role."""
    creds = CREDENTIALS.get(role)
    if not creds:
        pytest.skip(f"No credentials for role: {role}")
    
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=creds)
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Login failed for {role}: {response.status_code}")


class TestAIAnalysisAccessCheck:
    """Test /api/ai-analysis/access-check endpoint."""
    
    def test_admin_has_access(self, api_client):
        """Admin should have access to AI Analysis."""
        token = get_auth_token(api_client, "admin")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/access-check",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] == True
        assert data["role"] == "admin"
        print(f"✓ Admin has_access: {data['has_access']}, role: {data['role']}")
    
    def test_manager_has_access(self, api_client):
        """Manager should have access to AI Analysis."""
        token = get_auth_token(api_client, "manager")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/access-check",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] == True
        assert data["role"] == "manager"
        print(f"✓ Manager has_access: {data['has_access']}, role: {data['role']}")
    
    def test_operator_no_access(self, api_client):
        """Operator should NOT have access to AI Analysis."""
        token = get_auth_token(api_client, "operator")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/access-check",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] == False
        assert data["role"] == "operator"
        print(f"✓ Operator has_access: {data['has_access']}, role: {data['role']}")
    
    def test_viewer_no_access(self, api_client):
        """Viewer should NOT have access to AI Analysis."""
        token = get_auth_token(api_client, "viewer")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/access-check",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] == False
        assert data["role"] == "viewer"
        print(f"✓ Viewer has_access: {data['has_access']}, role: {data['role']}")
    
    def test_unauthenticated_returns_401(self, api_client):
        """Unauthenticated request should return 401."""
        response = api_client.get(f"{BASE_URL}/api/ai-analysis/access-check")
        assert response.status_code == 401
        print("✓ Unauthenticated request returns 401")


class TestAIAnalysisAnalyzeEndpoint:
    """Test /api/ai-analysis/analyze endpoint."""
    
    def test_admin_can_analyze(self, api_client):
        """Admin should be able to run AI analysis."""
        token = get_auth_token(api_client, "admin")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "orders" in data
        assert "total_analyzed" in data["summary"]
        assert "critical_count" in data["summary"]
        assert "medium_count" in data["summary"]
        assert "low_count" in data["summary"]
        print(f"✓ Admin analysis: {data['summary']['total_analyzed']} orders analyzed")
        print(f"  Critical: {data['summary']['critical_count']}, Medium: {data['summary']['medium_count']}, Low: {data['summary']['low_count']}")
    
    def test_manager_can_analyze(self, api_client):
        """Manager should be able to run AI analysis."""
        token = get_auth_token(api_client, "manager")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "orders" in data
        print(f"✓ Manager analysis: {data['summary']['total_analyzed']} orders analyzed")
    
    def test_operator_forbidden(self, api_client):
        """Operator should get 403 Forbidden."""
        token = get_auth_token(api_client, "operator")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        print("✓ Operator correctly gets 403 Forbidden for analyze")
    
    def test_viewer_forbidden(self, api_client):
        """Viewer should get 403 Forbidden."""
        token = get_auth_token(api_client, "viewer")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        print("✓ Viewer correctly gets 403 Forbidden for analyze")
    
    def test_unauthenticated_returns_401(self, api_client):
        """Unauthenticated request should return 401."""
        response = api_client.get(f"{BASE_URL}/api/ai-analysis/analyze")
        assert response.status_code == 401
        print("✓ Unauthenticated request returns 401")


class TestAIAnalysisExecuteEndpoint:
    """Test /api/ai-analysis/execute endpoint."""
    
    def test_admin_can_execute_action(self, api_client):
        """Admin should be able to execute AI-suggested actions."""
        token = get_auth_token(api_client, "admin")
        
        # Execute a test action
        response = api_client.post(
            f"{BASE_URL}/api/ai-analysis/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action_id": "send_reminder",
                "customer": "Test Customer",
                "order_analysis_id": "test-analysis-123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        print(f"✓ Admin executed action: {data['result']['message']}")
    
    def test_manager_can_execute_action(self, api_client):
        """Manager should be able to execute AI-suggested actions."""
        token = get_auth_token(api_client, "manager")
        
        response = api_client.post(
            f"{BASE_URL}/api/ai-analysis/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action_id": "view_order",
                "customer": "Test Customer",
                "order_analysis_id": "test-analysis-456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"✓ Manager executed action: {data['result']['message']}")
    
    def test_operator_forbidden(self, api_client):
        """Operator should get 403 Forbidden."""
        token = get_auth_token(api_client, "operator")
        
        response = api_client.post(
            f"{BASE_URL}/api/ai-analysis/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action_id": "send_reminder",
                "customer": "Test Customer",
                "order_analysis_id": "test-analysis-789"
            }
        )
        
        assert response.status_code == 403
        print("✓ Operator correctly gets 403 Forbidden for execute")
    
    def test_viewer_forbidden(self, api_client):
        """Viewer should get 403 Forbidden."""
        token = get_auth_token(api_client, "viewer")
        
        response = api_client.post(
            f"{BASE_URL}/api/ai-analysis/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action_id": "send_reminder",
                "customer": "Test Customer",
                "order_analysis_id": "test-analysis-000"
            }
        )
        
        assert response.status_code == 403
        print("✓ Viewer correctly gets 403 Forbidden for execute")


class TestAIAnalysisResponseStructure:
    """Test the structure of AI Analysis responses."""
    
    def test_analysis_response_has_risk_cards(self, api_client):
        """Analysis response should have proper risk card structure."""
        token = get_auth_token(api_client, "admin")
        response = api_client.get(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check summary structure
        summary = data.get("summary", {})
        assert "total_analyzed" in summary
        assert "critical_count" in summary
        assert "medium_count" in summary
        assert "low_count" in summary
        assert "total_amount_at_risk" in summary
        
        # Check orders structure (if any orders exist)
        orders = data.get("orders", [])
        if len(orders) > 0:
            order = orders[0]
            assert "id" in order
            assert "customer" in order
            assert "amount_due" in order
            assert "days_overdue" in order
            assert "risk_level" in order
            assert order["risk_level"] in ["critical", "medium", "low"]
            assert "reasoning" in order
            assert "suggested_actions" in order
            
            # Check action structure
            if len(order["suggested_actions"]) > 0:
                action = order["suggested_actions"][0]
                assert "id" in action
                assert "label" in action
                assert "description" in action
                assert "severity" in action
            
            print(f"✓ Order structure valid: {order['customer']} - {order['risk_level']}")
        else:
            print("✓ No orders to analyze (structure check passed)")
        
        print(f"✓ Summary structure valid: {summary}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
