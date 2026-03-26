#!/usr/bin/env python3
"""Test script to verify quick login functionality for demo users."""

import requests
import sys

BASE_URL = 'http://localhost:8000/api'

# Demo users to test
DEMO_USERS = [
    ('admin@agenterp.com', 'admin123', 'Admin'),
    ('manager@agenterp.com', 'manager123', 'Manager'),
    ('operator@agenterp.com', 'operator123', 'Operator'),
    ('viewer@agenterp.com', 'viewer123', 'Viewer'),
]

def test_login(email, password, label):
    """Test login for a single demo user."""
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            json={'email': email, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                token = data.get('access_token')
                user_role = data.get('user', {}).get('role')
                print(f"✅ {label:12} ({email:30}) - Login successful")
                return True
            else:
                print(f"❌ {label:12} ({email:30}) - Status error: {data.get('message')}")
                return False
        else:
            print(f"❌ {label:12} ({email:30}) - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {label:12} ({email:30}) - Error: {str(e)}")
        return False

def main():
    print("Testing Quick Login for Demo Users")
    print("=" * 70)
    
    results = []
    for email, password, label in DEMO_USERS:
        success = test_login(email, password, label)
        results.append(success)
    
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"\n✅ All {total} demo users can login successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {passed}/{total} demo users can login")
        sys.exit(1)

if __name__ == '__main__':
    main()
