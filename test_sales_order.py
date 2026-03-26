#!/usr/bin/env python3
"""Test sales order creation with IIM Bangalore company."""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def login_as_operator():
    """Login as operator to get token."""
    response = requests.post(
        f'{BASE_URL}/auth/login',
        json={'email': 'operator@agenterp.com', 'password': 'operator123'},
        timeout=5
    )
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def create_sales_order(token):
    """Create a sales order for IIM Bangalore."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "doctype": "Sales Order",
        "customer": "IIM Bangalore",
        "transaction_date": "2026-03-25",
        "items": [
            {"item_code": "SKU001", "qty": 200}
        ]
    }
    
    response = requests.post(
        f'{BASE_URL}/erp/sales-order',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    return response.status_code, response.json()

def main():
    print("Testing Sales Order Creation")
    print("=" * 70)
    
    print("Step 1: Login as operator...")
    token = login_as_operator()
    if not token:
        print("❌ Failed to login!")
        return False
    print("✅ Login successful")
    
    print("\nStep 2: Creating sales order for IIM Bangalore...")
    status_code, response = create_sales_order(token)
    
    print(f"Status Code: {status_code}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status_code == 200 and response.get('status') == 'success':
        print("\n✅ Sales order created successfully!")
        return True
    else:
        print("\n❌ Failed to create sales order")
        return False

if __name__ == '__main__':
    main()
