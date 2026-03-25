"""
Test Company-Based Data Segregation (Multi-Tenancy)
Tests for:
- Login with different company users
- /api/insights endpoint returns company-filtered data
- /api/insights/suggestions returns company-specific suggestions
- Different users see different company data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials with company associations
TEST_USERS = {
    "admin": {"email": "admin@agenterp.com", "password": "admin123", "company": None},
    "manager": {"email": "manager@techcorp.com", "password": "manager123", "company": "TechCorp Solutions"},
    "operator": {"email": "operator@innovate.com", "password": "operator123", "company": "InnovateTech Pvt Ltd"},
    "viewer": {"email": "viewer@global.com", "password": "viewer123", "company": "Global Industries Ltd"},
}


class TestCompanyLogin:
    """Test login with different company users."""
    
    def test_admin_login_no_company(self):
        """Admin user should have no company (sees all data)."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["admin"]["email"],
            "password": TEST_USERS["admin"]["password"]
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        # Admin should have no company (null) - sees all data
        assert data["user"].get("company") is None, f"Admin should have no company, got: {data['user'].get('company')}"
        print(f"SUCCESS: Admin login - no company filter (sees all)")
    
    def test_manager_login_with_company(self):
        """Manager user should have TechCorp Solutions company."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["manager"]["email"],
            "password": TEST_USERS["manager"]["password"]
        })
        assert response.status_code == 200, f"Manager login failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["user"]["role"] == "manager"
        assert data["user"]["company"] == "TechCorp Solutions", f"Expected TechCorp Solutions, got: {data['user'].get('company')}"
        print(f"SUCCESS: Manager login - company: {data['user']['company']}")
    
    def test_operator_login_with_company(self):
        """Operator user should have InnovateTech Pvt Ltd company."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["operator"]["email"],
            "password": TEST_USERS["operator"]["password"]
        })
        assert response.status_code == 200, f"Operator login failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["user"]["role"] == "operator"
        assert data["user"]["company"] == "InnovateTech Pvt Ltd", f"Expected InnovateTech Pvt Ltd, got: {data['user'].get('company')}"
        print(f"SUCCESS: Operator login - company: {data['user']['company']}")
    
    def test_viewer_login_with_company(self):
        """Viewer user should have Global Industries Ltd company."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["viewer"]["email"],
            "password": TEST_USERS["viewer"]["password"]
        })
        assert response.status_code == 200, f"Viewer login failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["user"]["role"] == "viewer"
        assert data["user"]["company"] == "Global Industries Ltd", f"Expected Global Industries Ltd, got: {data['user'].get('company')}"
        print(f"SUCCESS: Viewer login - company: {data['user']['company']}")


class TestInsightsCompanyFiltering:
    """Test /api/insights endpoint returns company-filtered data."""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["admin"]["email"],
            "password": TEST_USERS["admin"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def manager_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["manager"]["email"],
            "password": TEST_USERS["manager"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def operator_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["operator"]["email"],
            "password": TEST_USERS["operator"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def viewer_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["viewer"]["email"],
            "password": TEST_USERS["viewer"]["password"]
        })
        return response.json()["access_token"]
    
    def test_insights_admin_no_company_filter(self, admin_token):
        """Admin should see insights without company filter."""
        response = requests.get(
            f"{BASE_URL}/api/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Insights failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "insights" in data
        # Admin should have no company filter
        assert data.get("company_filter") is None, f"Admin should have no company filter, got: {data.get('company_filter')}"
        print(f"SUCCESS: Admin insights - no company filter, {len(data['insights'])} insights")
    
    def test_insights_manager_company_filter(self, manager_token):
        """Manager should see insights filtered by TechCorp Solutions."""
        response = requests.get(
            f"{BASE_URL}/api/insights",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200, f"Insights failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "insights" in data
        # Manager should have company filter
        assert data.get("company_filter") == "TechCorp Solutions", f"Expected TechCorp Solutions filter, got: {data.get('company_filter')}"
        print(f"SUCCESS: Manager insights - company filter: {data.get('company_filter')}, {len(data['insights'])} insights")
    
    def test_insights_operator_company_filter(self, operator_token):
        """Operator should see insights filtered by InnovateTech Pvt Ltd."""
        response = requests.get(
            f"{BASE_URL}/api/insights",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == 200, f"Insights failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "insights" in data
        # Operator should have company filter
        assert data.get("company_filter") == "InnovateTech Pvt Ltd", f"Expected InnovateTech Pvt Ltd filter, got: {data.get('company_filter')}"
        print(f"SUCCESS: Operator insights - company filter: {data.get('company_filter')}, {len(data['insights'])} insights")
    
    def test_insights_viewer_company_filter(self, viewer_token):
        """Viewer should see insights filtered by Global Industries Ltd."""
        response = requests.get(
            f"{BASE_URL}/api/insights",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200, f"Insights failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "insights" in data
        # Viewer should have company filter
        assert data.get("company_filter") == "Global Industries Ltd", f"Expected Global Industries Ltd filter, got: {data.get('company_filter')}"
        print(f"SUCCESS: Viewer insights - company filter: {data.get('company_filter')}, {len(data['insights'])} insights")
    
    def test_insights_without_auth_returns_401(self):
        """Insights endpoint should require authentication."""
        response = requests.get(f"{BASE_URL}/api/insights")
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print("SUCCESS: Insights endpoint requires authentication")


class TestSuggestionsCompanyFiltering:
    """Test /api/insights/suggestions endpoint returns company-specific suggestions."""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["admin"]["email"],
            "password": TEST_USERS["admin"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def manager_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["manager"]["email"],
            "password": TEST_USERS["manager"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def operator_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["operator"]["email"],
            "password": TEST_USERS["operator"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def viewer_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["viewer"]["email"],
            "password": TEST_USERS["viewer"]["password"]
        })
        return response.json()["access_token"]
    
    def test_suggestions_admin_no_company(self, admin_token):
        """Admin should get suggestions without company filter."""
        response = requests.get(
            f"{BASE_URL}/api/insights/suggestions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Suggestions failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert data["user_role"] == "admin"
        assert data.get("company") is None, f"Admin should have no company, got: {data.get('company')}"
        print(f"SUCCESS: Admin suggestions - no company, {len(data['suggestions'])} suggestions")
    
    def test_suggestions_manager_with_company(self, manager_token):
        """Manager should get suggestions filtered by TechCorp Solutions."""
        response = requests.get(
            f"{BASE_URL}/api/insights/suggestions",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200, f"Suggestions failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert data["user_role"] == "manager"
        assert data.get("company") == "TechCorp Solutions", f"Expected TechCorp Solutions, got: {data.get('company')}"
        print(f"SUCCESS: Manager suggestions - company: {data.get('company')}, {len(data['suggestions'])} suggestions")
    
    def test_suggestions_operator_with_company(self, operator_token):
        """Operator should get suggestions filtered by InnovateTech Pvt Ltd."""
        response = requests.get(
            f"{BASE_URL}/api/insights/suggestions",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == 200, f"Suggestions failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert data["user_role"] == "operator"
        assert data.get("company") == "InnovateTech Pvt Ltd", f"Expected InnovateTech Pvt Ltd, got: {data.get('company')}"
        print(f"SUCCESS: Operator suggestions - company: {data.get('company')}, {len(data['suggestions'])} suggestions")
    
    def test_suggestions_viewer_with_company(self, viewer_token):
        """Viewer should get suggestions filtered by Global Industries Ltd."""
        response = requests.get(
            f"{BASE_URL}/api/insights/suggestions",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200, f"Suggestions failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert data["user_role"] == "viewer"
        assert data.get("company") == "Global Industries Ltd", f"Expected Global Industries Ltd, got: {data.get('company')}"
        print(f"SUCCESS: Viewer suggestions - company: {data.get('company')}, {len(data['suggestions'])} suggestions")
    
    def test_suggestions_without_auth_returns_401(self):
        """Suggestions endpoint should require authentication."""
        response = requests.get(f"{BASE_URL}/api/insights/suggestions")
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print("SUCCESS: Suggestions endpoint requires authentication")
    
    def test_suggestions_structure(self, manager_token):
        """Verify suggestions have correct structure."""
        response = requests.get(
            f"{BASE_URL}/api/insights/suggestions",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["suggestions"]) > 0:
            suggestion = data["suggestions"][0]
            assert "id" in suggestion, "Suggestion should have id"
            assert "type" in suggestion, "Suggestion should have type"
            assert "text" in suggestion, "Suggestion should have text"
            assert "prompt" in suggestion, "Suggestion should have prompt"
            assert "priority" in suggestion, "Suggestion should have priority"
            print(f"SUCCESS: Suggestion structure verified - {suggestion['text'][:50]}...")
        else:
            print("INFO: No suggestions returned (may be expected based on ERP data)")


class TestAuthMeCompanyInfo:
    """Test /api/auth/me returns company info."""
    
    def test_auth_me_returns_company_for_manager(self):
        """GET /api/auth/me should return company info for manager."""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["manager"]["email"],
            "password": TEST_USERS["manager"]["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get user info
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data["user"]["company"] == "TechCorp Solutions"
        print(f"SUCCESS: Auth me returns company: {data['user']['company']}")
    
    def test_auth_me_returns_null_company_for_admin(self):
        """GET /api/auth/me should return null company for admin."""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USERS["admin"]["email"],
            "password": TEST_USERS["admin"]["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get user info
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data["user"].get("company") is None
        print("SUCCESS: Auth me returns null company for admin")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
