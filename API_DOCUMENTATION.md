# AgentERP API Documentation

Complete API reference for AgentERP backend endpoints.

---

## Authentication

Currently, the API is open for development. For production deployment, implement API key authentication:

```bash
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Health Check

Check API and ERPNext connection status.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "erp_mode": "mock",
  "erp_url": "https://demo.erpnext.com"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Agent Orchestration

Main endpoint for AI agent interactions. Processes structured requests and orchestrates ERPNext operations.

**Endpoint:** `POST /api/agent`

**Request Body:**
```json
{
  "intent": "create_sales_order",
  "customer": "ACME Corp",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 3
    }
  ],
  "transaction_date": "2026-03-06",
  "customer_data": {
    "customer_name": "ACME Corp",
    "customer_type": "Company",
    "territory": "India"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent` | string | Yes | Operation type: `create_sales_order`, `check_customer`, `create_customer` |
| `customer` | string | Conditional | Customer name (required for all operations) |
| `items` | array | Conditional | List of items (required for `create_sales_order`) |
| `transaction_date` | string | No | Date in YYYY-MM-DD format (defaults to today) |
| `customer_data` | object | Conditional | Customer details (required for `create_customer`) |

**Response (Success):**
```json
{
  "status": "success",
  "message": "Sales Order SO-20260306-A3F2B1 created successfully",
  "data": {
    "name": "SO-20260306-A3F2B1",
    "customer": "ACME Corp",
    "transaction_date": "2026-03-06",
    "items": [
      {
        "item_code": "ITEM-001",
        "qty": 3
      }
    ],
    "total_qty": 3,
    "status": "Draft"
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Customer not found"
}
```

**Status Codes:**
- `200 OK` - Request processed successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server error

**Examples:**

**Create Sales Order:**
```bash
curl -X POST https://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "create_sales_order",
    "customer": "ACME Corp",
    "items": [{"item_code": "ITEM-001", "qty": 5}],
    "transaction_date": "2026-03-06"
  }'
```

**Check Customer:**
```bash
curl -X POST https://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "check_customer",
    "customer": "TechCorp Inc"
  }'
```

**Create Customer:**
```bash
curl -X POST https://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "create_customer",
    "customer_data": {
      "customer_name": "Global Solutions",
      "customer_type": "Company",
      "territory": "India"
    }
  }'
```

---

### 3. Check Customer

Check if a customer exists in ERPNext.

**Endpoint:** `GET /api/customer/{customer_name}`

**Path Parameters:**
- `customer_name` (string) - Name of the customer to check

**Response:**
```json
{
  "status": "success",
  "exists": true,
  "data": {
    "name": "ACME Corp",
    "customer_type": "Company",
    "territory": "India"
  }
}
```

**Example:**
```bash
curl https://localhost:8000/api/customer/ACME%20Corp
```

---

### 4. Create Customer

Create a new customer in ERPNext.

**Endpoint:** `POST /api/customer`

**Request Body:**
```json
{
  "doctype": "Customer",
  "customer_name": "Global Solutions",
  "customer_type": "Company",
  "territory": "India"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doctype` | string | Yes | Always "Customer" |
| `customer_name` | string | Yes | Customer name |
| `customer_type` | string | Yes | "Company" or "Individual" |
| `territory` | string | Yes | Territory name |

**Response:**
```json
{
  "status": "success",
  "message": "Customer 'Global Solutions' created successfully",
  "data": {
    "name": "Global Solutions",
    "customer_type": "Company",
    "territory": "India",
    "creation": "2026-03-06T10:30:00Z"
  }
}
```

**Example:**
```bash
curl -X POST https://localhost:8000/api/customer \
  -H "Content-Type: application/json" \
  -d '{
    "doctype": "Customer",
    "customer_name": "New Customer Ltd",
    "customer_type": "Company",
    "territory": "India"
  }'
```

---

### 5. Create Sales Order

Create a sales order in ERPNext.

**Endpoint:** `POST /api/sales-order`

**Request Body:**
```json
{
  "doctype": "Sales Order",
  "customer": "ACME Corp",
  "transaction_date": "2026-03-06",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 3
    },
    {
      "item_code": "ITEM-002",
      "qty": 5
    }
  ]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doctype` | string | Yes | Always "Sales Order" |
| `customer` | string | Yes | Customer name |
| `transaction_date` | string | Yes | Date in YYYY-MM-DD format |
| `items` | array | Yes | Array of item objects |
| `items[].item_code` | string | Yes | Item code |
| `items[].qty` | integer | Yes | Quantity |

**Response:**
```json
{
  "status": "success",
  "message": "Sales Order SO-20260306-A3F2B1 created successfully",
  "data": {
    "name": "SO-20260306-A3F2B1",
    "customer": "ACME Corp",
    "transaction_date": "2026-03-06",
    "items": [
      {"item_code": "ITEM-001", "qty": 3},
      {"item_code": "ITEM-002", "qty": 5}
    ],
    "total_qty": 8,
    "status": "Draft"
  }
}
```

**Example:**
```bash
curl -X POST https://localhost:8000/api/sales-order \
  -H "Content-Type: application/json" \
  -d '{
    "doctype": "Sales Order",
    "customer": "ACME Corp",
    "transaction_date": "2026-03-06",
    "items": [
      {"item_code": "LAPTOP-001", "qty": 2},
      {"item_code": "MOUSE-001", "qty": 2}
    ]
  }'
```

---

### 6. Save Chat Message

Store a chat message in the database.

**Endpoint:** `POST /api/chat/messages`

**Request Body:**
```json
{
  "role": "user",
  "content": "Create a sales order for ACME Corp",
  "type": "text",
  "widget_data": null
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | "user" or "assistant" |
| `content` | string | Yes | Message content |
| `type` | string | Yes | "text" or "widget" |
| `widget_data` | object | No | Additional widget data |

**Response:**
```json
{
  "status": "success"
}
```

---

### 7. Get Chat History

Retrieve chat message history.

**Endpoint:** `GET /api/chat/messages`

**Response:**
```json
[
  {
    "id": "uuid-1",
    "role": "user",
    "content": "Create a sales order for ACME Corp",
    "type": "text",
    "widget_data": null,
    "timestamp": "2026-03-06T10:30:00Z"
  },
  {
    "id": "uuid-2",
    "role": "assistant",
    "content": "Sales Order created successfully",
    "type": "widget",
    "widget_data": {
      "type": "sales_order",
      "name": "SO-20260306-A3F2B1"
    },
    "timestamp": "2026-03-06T10:30:05Z"
  }
]
```

---

## Data Models

### AgentRequest

```typescript
interface AgentRequest {
  intent: 'create_sales_order' | 'check_customer' | 'create_customer';
  customer?: string;
  items?: Array<{
    item_code: string;
    qty: number;
  }>;
  transaction_date?: string;  // YYYY-MM-DD
  customer_data?: {
    customer_name: string;
    customer_type: 'Company' | 'Individual';
    territory: string;
  };
}
```

### AgentResponse

```typescript
interface AgentResponse {
  status: 'success' | 'error';
  message: string;
  data?: any;
}
```

### Customer

```typescript
interface Customer {
  doctype: 'Customer';
  customer_name: string;
  customer_type: 'Company' | 'Individual';
  territory: string;
}
```

### SalesOrder

```typescript
interface SalesOrder {
  doctype: 'Sales Order';
  customer: string;
  transaction_date: string;  // YYYY-MM-DD
  items: Array<{
    item_code: string;
    qty: number;
  }>;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "message": "Detailed error message",
  "detail": "Additional error details"
}
```

### Common Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Missing required parameters |
| 404 | Not Found | Customer or item not found |
| 422 | Validation Error | Invalid data format |
| 500 | Internal Server Error | Server or ERP system error |

---

## Rate Limits

Currently no rate limits are enforced. For production deployment, implement:

- **Per User**: 100 requests per minute
- **Per IP**: 1000 requests per hour

---

## Webhooks (Future Feature)

Subscribe to ERP events:

```json
{
  "event": "sales_order.created",
  "webhook_url": "https://your-app.com/webhooks/erp",
  "secret": "your_webhook_secret"
}
```

---

## Mock Mode

When `ERP_MOCK_MODE=true`, all ERPNext operations are simulated:

**Mock Customers:**
- ACME Corp
- TechCorp Inc
- Global Solutions

**Mock Items:**
- ITEM-001
- LAPTOP-001
- MOUSE-001

**Mock Behavior:**
- Customer checks: Returns success for mock customers
- Sales orders: Generates random order IDs
- API delays: Simulates network latency (0.5-1.5s)

---

## Best Practices

1. **Always validate customer existence** before creating sales orders
2. **Use transaction dates** in YYYY-MM-DD format
3. **Handle errors gracefully** - API may return ERP-specific errors
4. **Implement retry logic** for transient failures
5. **Cache customer data** to reduce API calls
6. **Use batch operations** when possible (future feature)

---

## Examples in Different Languages

### Python

```python
import requests

url = "https://localhost:8000/api/agent"
payload = {
    "intent": "create_sales_order",
    "customer": "ACME Corp",
    "items": [{"item_code": "ITEM-001", "qty": 3}],
    "transaction_date": "2026-03-06"
}

response = requests.post(url, json=payload)
print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const url = 'https://localhost:8000/api/agent';
const data = {
  intent: 'create_sales_order',
  customer: 'ACME Corp',
  items: [{ item_code: 'ITEM-001', qty: 3 }],
  transaction_date: '2026-03-06'
};

axios.post(url, data)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

### cURL

```bash
curl -X POST https://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "create_sales_order",
    "customer": "ACME Corp",
    "items": [{"item_code": "ITEM-001", "qty": 3}],
    "transaction_date": "2026-03-06"
  }'
```

---

## Support

For API issues or questions:
- Check this documentation
- Review main README.md
- Check backend logs: `/var/log/supervisor/backend.err.log`

---

**Last Updated**: March 6, 2026  
**API Version**: 1.0.0
