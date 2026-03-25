# AgentERP Hackathon Demo - API Reference

## Seed Endpoints

### 1. Seed Full Demo Data

**Endpoint:** `POST /api/auth/seed-demo`

**Description:** Seeds comprehensive demo scenario including users, ERPNext customers, sales orders, chat history, and audit logs.

**Parameters:**
```
reset (boolean, optional): Whether to clear existing data first (default: true)
```

**Request:**
```bash
curl -X POST http://localhost:8001/api/auth/seed-demo \
  -H "Content-Type: application/json"
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Demo seeding complete",
  "summary": {
    "users_created": 4,
    "customers_created": 6,
    "orders_created": 6,
    "chat_sessions": 3,
    "chat_messages": 15,
    "approval_requests": 3,
    "audit_logs": 8,
    "dashboard_metrics": 1
  }
}
```

**Response (Failure):**
```json
{
  "status": "error",
  "message": "Failed to seed demo data: [specific error]"
}
```

**Timing:** Takes 3-5 seconds

**What Gets Seeded:**

**Users (4):**
- admin@agenterp.com / admin123 (ADMIN role)
- manager@agenterp.com / manager123 (MANAGER role)
- operator@agenterp.com / operator123 (OPERATOR role)
- viewer@agenterp.com / viewer123 (VIEWER role)

**Customers (6):**
- Acme Manufacturing
- Global Tech Industries
- Innovation Labs Inc
- Enterprise Solutions Ltd
- Cloud Systems Partners
- Data Analytics Corp

**Sales Orders (6):**
- SO-2024-00101 (₹545K, pending approval)
- SO-2024-00102 (₹1,050K, approved)
- SO-2024-00103 (₹61K, submitted)
- SO-2024-00104 (₹620K, pending approval)
- SO-2024-00099 (₹210K, in-delivery)
- SO-2024-00095 (₹50K, completed)

**Total Value:** ₹2,536,000

**Chat Sessions (3):**
- Operator session: Order creation workflow
- Manager session: Approval workflow
- Admin session: Dashboard review

**Chat Messages (15):**
- 4 in operator session
- 6 in manager session
- 2 in admin session

**Audit Logs (8+):**
- Order creation events
- Approval flagging events
- Approval actions
- Query logs

---

### 2. Reset Demo Data

**Endpoint:** `POST /api/auth/reset-demo`

**Description:** Clears all seeded demo data from MongoDB. Data is irreversible—use before re-seeding.

**Request:**
```bash
curl -X POST http://localhost:8001/api/auth/reset-demo
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Demo data reset successfully. Data is ready for re-seeding."
}
```

**What Gets Cleared:**
- chat_sessions
- chat_messages
- sales_orders
- approval_requests
- audit_logs
- dashboard_metrics
- (NOT users - kept for reference)

**Typical Workflow:**
```bash
# Between demo runs
curl -X POST http://localhost:8001/api/auth/reset-demo
curl -X POST http://localhost:8001/api/auth/seed-demo
# Then refresh frontend
```

---

## Related Endpoints (Required for Demo)

### Authentication

#### Login
**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "operator@agenterp.com",
    "password": "operator123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "email": "operator@agenterp.com",
    "name": "Raj Patel",
    "role": "operator"
  }
}
```

#### Verify Token
**Endpoint:** `GET /api/auth/verify`

```bash
curl -X GET http://localhost:8001/api/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Sales Orders

#### List Sales Orders
**Endpoint:** `POST /api/entity`

```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@agenterp.com","password":"operator123"}' \
  | jq -r '.access_token')

curl -X POST http://localhost:8001/api/entity \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "query",
    "doctype": "Sales Order",
    "limit": 20,
    "filters": [["grand_total", ">", 50000]]
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "SO-2024-00101",
      "order_id": "SO-2024-00101",
      "customer": "Global Tech Industries",
      "grand_total": 545000,
      "status": "pending_approval",
      "transaction_date": "2024-01-02T10:00:00Z",
      "items": [...]
    },
    ...
  ]
}
```

---

### Approvals

#### List Pending Approvals (Manager)
**Endpoint:** `GET /api/approvals`

```bash
MANAGER_TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@agenterp.com","password":"manager123"}' \
  | jq -r '.access_token')

curl -X GET "http://localhost:8001/api/approvals" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "approval-1",
      "order_id": "SO-2024-00101",
      "customer": "Global Tech Industries",
      "order_value": 545000,
      "status": "pending",
      "created_at": "2024-01-02T10:00:00Z",
      "requester_email": "operator@agenterp.com"
    },
    ...
  ]
}
```

#### Approve an Order
**Endpoint:** `POST /api/approvals/{id}/approve`

```bash
curl -X POST "http://localhost:8001/api/approvals/approval-1/approve" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approval_notes": "Approved based on excellent credit history"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Order approved successfully",
  "data": {
    "id": "approval-1",
    "order_id": "SO-2024-00101",
    "status": "approved",
    "approved_by": "manager@agenterp.com",
    "approved_at": "2024-01-03T15:45:00Z"
  }
}
```

---

### Audit Logs

#### Get Audit Logs
**Endpoint:** `GET /api/audit`

```bash
curl -X GET "http://localhost:8001/api/audit?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

**Query Parameters:**
- `limit` (integer): Number of logs to return (default: 50)
- `offset` (integer): Pagination offset (default: 0)
- `action` (string): Filter by action type
- `user_email` (string): Filter by user
- `resource_type` (string): Filter by resource type

**Response:**
```json
{
  "status": "success",
  "total": 12,
  "data": [
    {
      "id": "log-1",
      "user_id": "user-operator",
      "user_email": "operator@agenterp.com",
      "user_role": "operator",
      "action": "create_order",
      "resource_type": "Sales Order",
      "resource_id": "SO-2024-00101",
      "timestamp": "2024-01-02T14:51:00Z",
      "result": "success",
      "result_message": "Order created successfully"
    },
    {
      "id": "log-2",
      "user_id": "system",
      "user_email": "system@agenterp.com",
      "user_role": "admin",
      "action": "request_approval",
      "resource_type": "Sales Order",
      "resource_id": "SO-2024-00101",
      "timestamp": "2024-01-02T14:52:00Z",
      "result": "success",
      "result_message": "High-value order flagged for approval"
    },
    ...
  ]
}
```

---

### Chat

#### Create Chat Session
**Endpoint:** `POST /api/chat/sessions`

```bash
curl -X POST http://localhost:8001/api/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "status": "success",
  "session": {
    "id": "session-abc123",
    "user_id": "user-id",
    "user_email": "operator@agenterp.com",
    "created_at": "2024-01-03T10:00:00Z",
    "title": "New Chat"
  }
}
```

#### Get Chat Messages
**Endpoint:** `GET /api/chat/sessions/{session_id}/messages`

```bash
curl -X GET "http://localhost:8001/api/chat/sessions/session-001/messages" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "msg-1",
      "session_id": "session-001",
      "role": "user",
      "content": "Create a sales order for Global Tech Industries...",
      "timestamp": "2024-01-02T14:46:00Z"
    },
    {
      "id": "msg-2",
      "session_id": "session-001",
      "role": "assistant",
      "content": "📋 I've created sales order SO-2024-00101...",
      "timestamp": "2024-01-02T14:46:30Z"
    },
    ...
  ]
}
```

---

## Demo Data Constants

### Approval Threshold
```python
HIGH_VALUE_ORDER_THRESHOLD = 50000  # ₹50,000
```
Orders above this value are automatically flagged for approval.

### Demo Base Time
All demo data is timestamped relative to:
```python
DEMO_BASE_TIME = datetime.now(timezone.utc) - timedelta(days=7)
```
This creates realistic "past" timestamps for the scenario.

### User Roles
```
Admin:     Can approve any order, manage users, view all data
Manager:   Can approve orders, view pending approvals, view audit logs
Operator:  Can create orders, view own orders
Viewer:    Read-only access to all data
```

---

## Database Collections

### chat_sessions
```json
{
  "_id": "ObjectId",
  "id": "session-001",
  "created_at": "2024-01-02T10:00:00Z",
  "updated_at": "2024-01-02T10:30:00Z",
  "user_id": "user-operator",
  "user_email": "operator@agenterp.com",
  "title": "Order Creation Session",
  "company": "TechCorp Solutions"
}
```

### chat_messages
```json
{
  "_id": "ObjectId",
  "id": "msg-uuid",
  "session_id": "session-001",
  "role": "user|assistant",
  "content": "Chat message content",
  "timestamp": "2024-01-02T14:46:00Z",
  "type": "text"
}
```

### sales_orders
```json
{
  "_id": "ObjectId",
  "id": "SO-2024-00101",
  "order_id": "SO-2024-00101",
  "customer": "Global Tech Industries",
  "transaction_date": "2024-01-02T10:00:00Z",
  "items": [
    {
      "item_code": "SERVER-001",
      "item_name": "Enterprise Server",
      "qty": 2,
      "rate": 150000
    }
  ],
  "grand_total": 545000,
  "status": "pending_approval",
  "priority": "high",
  "operator": "operator@agenterp.com",
  "approval_required": true,
  "approval_status": "pending"
}
```

### approval_requests
```json
{
  "_id": "ObjectId",
  "id": "approval-uuid",
  "order_id": "SO-2024-00101",
  "customer": "Global Tech Industries",
  "order_value": 545000,
  "status": "pending|approved|rejected",
  "requester_email": "operator@agenterp.com",
  "requester_id": "user-operator",
  "created_at": "2024-01-02T10:00:00Z",
  "approved_by": "manager@agenterp.com",
  "approved_at": "2024-01-03T15:45:00Z",
  "reason": "Order value exceeds ₹50,000 threshold"
}
```

### audit_logs
```json
{
  "_id": "ObjectId",
  "id": "log-uuid",
  "user_id": "user-operator",
  "user_email": "operator@agenterp.com",
  "user_role": "operator",
  "action": "create_order|approve_request|query_data",
  "resource_type": "Sales Order|Approval Request|Audit Log",
  "resource_id": "SO-2024-00101",
  "timestamp": "2024-01-02T14:51:00Z",
  "result": "success|failure|pending",
  "result_message": "Order created successfully",
  "company": "TechCorp Solutions"
}
```

---

## Common Demo Flows (cURL)

### Complete Login → Create Order → Approve Flow

```bash
#!/bin/bash

# Step 1: OPERATOR LOGIN
echo "=== Operator Login ==="
OPERATOR_LOGIN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "operator@agenterp.com",
    "password": "operator123"
  }')

OPERATOR_TOKEN=$(echo $OPERATOR_LOGIN | jq -r '.access_token')
echo "Token: $OPERATOR_TOKEN"

# Step 2: LIST SALES ORDERS
echo -e "\n=== List All Orders ==="
curl -s -X POST http://localhost:8001/api/entity \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "query",
    "doctype": "Sales Order",
    "limit": 10
  }' | jq '.data | length'

# Step 3: MANAGER LOGIN
echo -e "\n=== Manager Login ==="
MANAGER_LOGIN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@agenterp.com",
    "password": "manager123"
  }')

MANAGER_TOKEN=$(echo $MANAGER_LOGIN | jq -r '.access_token')

# Step 4: GET PENDING APPROVALS
echo -e "\n=== Pending Approvals ==="
APPROVALS=$(curl -s -X GET http://localhost:8001/api/approvals \
  -H "Authorization: Bearer $MANAGER_TOKEN")

APPROVAL_ID=$(echo $APPROVALS | jq -r '.data[0].id')
echo "First approval ID: $APPROVAL_ID"

# Step 5: APPROVE ORDER
echo -e "\n=== Approving Order ==="
curl -s -X POST "http://localhost:8001/api/approvals/$APPROVAL_ID/approve" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approval_notes": "Approved in demo"
  }' | jq '.status'

# Step 6: CHECK AUDIT LOG
echo -e "\n=== Recent Audit Logs ==="
curl -s -X GET "http://localhost:8001/api/audit?limit=5" \
  -H "Authorization: Bearer $MANAGER_TOKEN" | jq '.data | length'

echo -e "\n✅ Demo flow complete!"
```

---

## Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Order created |
| 201 | Created | New approval request |
| 400 | Bad request | Invalid order data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permission |
| 404 | Not found | Order doesn't exist |
| 500 | Server error | Database connection failed |

---

## Rate Limiting

No rate limiting on demo endpoints. For production, implement:
- `/api/auth/login`: 10 req/min per IP
- `/api/auth/seed-demo`: 1 req/hour (admin only)
- Other endpoints: 100 req/min per user

---

## Security Notes

**For Demo:**
- Admin token gives full access
- All endpoints use Bearer token auth
- CORS enabled for localhost:3000

**For Production:**
- Use HTTPS only
- Implement rate limiting
- Add IP allowlisting for seeding endpoints
- Use environment variables for secrets
- Implement API key rotation

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0.0  
**Status:** Stable for Demo
