"""
Enterprise Authentication and Authorization Tests
Tests for: Auth, Insights, Audit, Approvals endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USERS = {
    'admin': {'email': 'admin@agenterp.com', 'password': 'admin123'},
    'manager': {'email': 'manager@agenterp.com', 'password': 'manager123'},
    'operator': {'email': 'operator@agenterp.com', 'password': 'operator123'},
    'viewer': {'email': 'viewer@agenterp.com', 'password': 'viewer123'},
}


@pytest.fixture(scope='module')
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    return session


@pytest.fixture(scope='module')
def manager_token(api_client):
    """Get manager authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        'email': TEST_USERS['manager']['email'],
        'password': TEST_USERS['manager']['password']
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    pytest.skip("Manager authentication failed")


@pytest.fixture(scope='module')
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        'email': TEST_USERS['admin']['email'],
        'password': TEST_USERS['admin']['password']
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope='module')
def viewer_token(api_client):
    """Get viewer authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        'email': TEST_USERS['viewer']['email'],
        'password': TEST_USERS['viewer']['password']
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    pytest.skip("Viewer authentication failed")


class TestHealthEndpoint:
    """Health check tests"""
    
    def test_health_check(self, api_client):
        """Test /api/health returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'erp_mode' in data


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_login_manager_success(self, api_client):
        """Test POST /api/auth/login with manager credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            'email': TEST_USERS['manager']['email'],
            'password': TEST_USERS['manager']['password']
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data['status'] == 'success'
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert 'user' in data
        
        # Verify user data
        user = data['user']
        assert user['email'] == TEST_USERS['manager']['email']
        assert user['role'] == 'manager'
        assert user['name'] == 'Manager User'
        assert 'id' in user
    
    def test_login_admin_success(self, api_client):
        """Test POST /api/auth/login with admin credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            'email': TEST_USERS['admin']['email'],
            'password': TEST_USERS['admin']['password']
        })
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['user']['role'] == 'admin'
    
    def test_login_operator_success(self, api_client):
        """Test POST /api/auth/login with operator credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            'email': TEST_USERS['operator']['email'],
            'password': TEST_USERS['operator']['password']
        })
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['user']['role'] == 'operator'
    
    def test_login_viewer_success(self, api_client):
        """Test POST /api/auth/login with viewer credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            'email': TEST_USERS['viewer']['email'],
            'password': TEST_USERS['viewer']['password']
        })
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['user']['role'] == 'viewer'
    
    def test_login_invalid_credentials(self, api_client):
        """Test POST /api/auth/login with invalid credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    def test_get_me_with_valid_token(self, api_client, manager_token):
        """Test GET /api/auth/me with valid token"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'user' in data
        assert data['user']['email'] == TEST_USERS['manager']['email']
        assert data['user']['role'] == 'manager'
    
    def test_get_me_without_token(self, api_client):
        """Test GET /api/auth/me without token returns 401"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
    
    def test_verify_token_valid(self, api_client, manager_token):
        """Test GET /api/auth/verify with valid token"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/verify",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['valid'] == True
        assert 'user' in data


class TestInsightsEndpoints:
    """Proactive Insights endpoint tests"""
    
    def test_get_insights_authenticated(self, api_client, manager_token):
        """Test GET /api/insights returns insights for authenticated user"""
        response = api_client.get(
            f"{BASE_URL}/api/insights",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'insights' in data
        assert isinstance(data['insights'], list)
        assert 'generated_at' in data
        assert data['user_role'] == 'manager'
    
    def test_get_insights_unauthenticated(self, api_client):
        """Test GET /api/insights without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/insights")
        assert response.status_code == 401
    
    def test_get_public_insights(self, api_client):
        """Test GET /api/insights/public works without strict auth"""
        response = api_client.get(f"{BASE_URL}/api/insights/public")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'insights' in data
    
    def test_get_business_impact(self, api_client, manager_token):
        """Test GET /api/insights/impact returns business metrics"""
        response = api_client.get(
            f"{BASE_URL}/api/insights/impact",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'metrics' in data
        assert 'summary' in data
        
        # Verify metrics structure
        metrics = data['metrics']
        assert 'total_actions_today' in metrics
        assert 'total_actions_month' in metrics
        assert 'efficiency_gain_percent' in metrics
        assert 'projected_monthly_savings_inr' in metrics
        
        # Verify summary structure
        summary = data['summary']
        assert 'headline' in summary
        assert 'time_saved' in summary
        assert 'cost_saved' in summary


class TestAuditEndpoints:
    """Audit log endpoint tests"""
    
    def test_get_audit_logs_authenticated(self, api_client, manager_token):
        """Test GET /api/audit returns audit logs"""
        response = api_client.get(
            f"{BASE_URL}/api/audit",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'logs' in data
        assert isinstance(data['logs'], list)
        assert 'total' in data
    
    def test_get_audit_logs_unauthenticated(self, api_client):
        """Test GET /api/audit without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/audit")
        assert response.status_code == 401
    
    def test_get_recent_activity(self, api_client, manager_token):
        """Test GET /api/audit/recent returns recent activity"""
        response = api_client.get(
            f"{BASE_URL}/api/audit/recent",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
    
    def test_get_audit_stats(self, api_client, manager_token):
        """Test GET /api/audit/stats returns statistics"""
        response = api_client.get(
            f"{BASE_URL}/api/audit/stats",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'


class TestApprovalsEndpoints:
    """Approval workflow endpoint tests"""
    
    def test_get_pending_approvals_manager(self, api_client, manager_token):
        """Test GET /api/approvals returns pending approvals for manager"""
        response = api_client.get(
            f"{BASE_URL}/api/approvals",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'approvals' in data
        assert isinstance(data['approvals'], list)
        assert 'count' in data
    
    def test_get_pending_approvals_viewer_forbidden(self, api_client, viewer_token):
        """Test GET /api/approvals returns 403 for viewer (non-manager)"""
        response = api_client.get(
            f"{BASE_URL}/api/approvals",
            headers={'Authorization': f'Bearer {viewer_token}'}
        )
        assert response.status_code == 403
    
    def test_get_pending_approvals_unauthenticated(self, api_client):
        """Test GET /api/approvals without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/approvals")
        assert response.status_code == 401
    
    def test_get_my_approval_requests(self, api_client, manager_token):
        """Test GET /api/approvals/my-requests returns user's requests"""
        response = api_client.get(
            f"{BASE_URL}/api/approvals/my-requests",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'


class TestRBACPermissions:
    """Role-Based Access Control tests"""
    
    def test_admin_can_list_users(self, api_client, admin_token):
        """Test admin can access /api/auth/users"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/users",
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'users' in data
        assert len(data['users']) >= 4  # At least 4 default users
    
    def test_manager_cannot_list_users(self, api_client, manager_token):
        """Test manager cannot access /api/auth/users (admin only)"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/users",
            headers={'Authorization': f'Bearer {manager_token}'}
        )
        assert response.status_code == 403
    
    def test_viewer_cannot_access_approvals(self, api_client, viewer_token):
        """Test viewer cannot access pending approvals"""
        response = api_client.get(
            f"{BASE_URL}/api/approvals",
            headers={'Authorization': f'Bearer {viewer_token}'}
        )
        assert response.status_code == 403


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
