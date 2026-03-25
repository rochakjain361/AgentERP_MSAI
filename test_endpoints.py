import requests

base_url = 'http://localhost:8003'

# Seed demo
print("Seeding demo...")
response = requests.post(f'{base_url}/api/auth/seed-demo')
print(response.json())

# Login as admin
print("Logging in...")
response = requests.post(f'{base_url}/api/auth/login', json={'email':'admin@agenterp.com','password':'admin123'})
print(response.json())
if response.status_code == 200:
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # List sales orders
    print("Listing sales orders...")
    response = requests.post(f'{base_url}/api/entity', json={
        "action": "query",
        "doctype": "Sales Order",
        "fields": ["name", "customer", "grand_total", "creation"],
        "limit": 10,
        "order_by": "creation desc"
    }, headers=headers)
    print(response.json())
    
    # List customers
    print("Listing customers...")
    response = requests.post(f'{base_url}/api/entity', json={
        "action": "query",
        "doctype": "Customer",
        "fields": ["name", "customer_name"],
        "limit": 50
    }, headers=headers)
    print(response.json())
    
    # Test AI chat
    print("Testing AI chat...")
    response = requests.post(f'{base_url}/api/chat', json={
        "message": "Hello, can you tell me about the system?"
    }, headers=headers)
    print(response.json())
else:
    print("Login failed")