# Demo Integration & Verification Guide

## Complete End-to-End Verification Checklist

Use this guide to verify every aspect of the hackathon demo works correctly.

---

## Section 1: Backend Setup & Health Check (5 min)

### 1.1 Start Backend
```bash
cd /Users/rochakjain/Desktop/Dev/MS-AgenticAI/backend
source venv/bin/activate
PYTHONPATH=/Users/rochakjain/Desktop/Dev/MS-AgenticAI/backend:/Users/rochakjain/Desktop/Dev/MS-AgenticAI/backend/venv/lib/python3.11/site-packages \
  /Users/rochakjain/Desktop/Dev/MS-AgenticAI/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### 1.2 Health Check
```bash
curl http://localhost:8001/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "erp_mode": "mock",
  "erp_url": "https://demo.erpnext.com"
}
```

✅ Backend is running

---

## Section 2: Seed Demo Data (3 min)

### 2.1 Seed Hackathon Demo
```bash
curl -X POST http://localhost:8001/api/auth/seed-demo
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Demo seeding complete",
  "summary": {
    "users_created": 4,
    "customers_created": 6,
    "orders_created": 6,
    "chat_sessions": 3,
    "audit_logs": 8
  }
}
```

### 2.2 Verify Users Created
```bash
curl -X GET http://localhost:8001/api/auth/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Or just verify login works
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "operator@agenterp.com", "password": "operator123"}'
```

**Expected:** All 4 demo users can login successfully

✅ Demo data seeded

---

## Section 3: API Endpoints Verification (5 min)

### 3.1 Authentication Endpoints

**Test: Register new user**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.user@agenterp.com",
    "password": "testpass123",
    "name": "Test User",
    "role": "operator"
  }'
```

Expected: Success response with token

**Test: Login**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "operator@agenterp.com",
    "password": "operator123"
  }'
```

Expected: Success with access_token

✅ Auth endpoints working

### 3.2 Sales Orders Endpoint

**Test: List sales orders**
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@agenterp.com","password":"operator123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl -X GET http://localhost:8001/api/entity \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "query",
    "doctype": "Sales Order",
    "limit": 10
  }'
```

Expected: 6 sales orders returned

✅ ERPNext integration ready

### 3.3 Chat Endpoints

**Test: Create chat session**
```bash
/* Get token first, see above */

curl -X POST http://localhost:8001/api/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

Expected: New chat session created

### 3.4 Approvals Endpoint

**Test: List pending approvals**
```bash
curl -X GET http://localhost:8001/api/approvals \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

Expected: 2-3 pending approvals returned

✅ Approval workflow ready

### 3.5 Audit Logs Endpoint

**Test: Get audit logs**
```bash
curl -X GET http://localhost:8001/api/audit?limit=10 \
  -H "Authorization: Bearer $TOKEN"
```

Expected: 8+ audit log entries

✅ Audit trail working

---

## Section 4: Frontend Setup & Integration (5 min)

### 4.1 Start Frontend
```bash
cd /Users/rochakjain/Desktop/Dev/MS-AgenticAI/frontend
npm start
```

Expected: Browser opens to http://localhost:3000

### 4.2 Login Test

**As Operator:**
- Email: `operator@agenterp.com`
- Password: `operator123`
- Expected: Dashboard shows chat interface

**Role Switcher:**
- If implemented, should show role selector
- Try switching to "Manager"
- Should see approvals panel

**As Manager:**
- Email: `manager@agenterp.com`
- Password: `manager123`
- Expected: Approvals panel shows 2-3 pending orders

### 4.3 Component Integration

Check if these components appear on dashboard:
- [ ] Chat Interface (should work for all roles)
- [ ] Role Switcher (quick role switching)
- [ ] Sales Order List / Approvals Panel (managers only)
- [ ] Audit Log Panel (all roles)
- [ ] Dashboard Metrics (orders, values, stats)

If components are missing, they need to be integrated into DashboardView. See section 5 below.

✅ Frontend running

---

## Section 5: Component Integration (if needed)

If role switcher, approvals panel, or audit panel are not visible, integrate them:

### 5.1 Update DashboardView

Edit: `frontend/src/components/DashboardView.js`

```javascript
import { useAuth } from '../contexts/AuthContext';
import RoleSwitcher from './RoleSwitcher';
import SalesOrderList from './SalesOrderList';
import AuditLogPanel from './AuditLogPanel';

export function DashboardView() {
  const { user } = useAuth();
  
  return (
    <div>
      {/* Header with role switcher */}
      <div className="header">
        <RoleSwitcher 
          currentUser={user}
          onRoleSwitch={handleRoleSwitch}
          onLogout={handleLogout}
        />
      </div>
      
      {/* Main content grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Chat interface */}
        <ChatInterface />
        
        {/* Approvals (manager/admin only) */}
        {(user?.role === 'manager' || user?.role === 'admin') && (
          <SalesOrderList user={user} />
        )}
        
        {/* Audit log (all users) */}
        <AuditLogPanel user={user} />
      </div>
    </div>
  );
}
```

### 5.2 Verify Component Files Exist

```bash
# Check if components are present
ls -la frontend/src/components/RoleSwitcher.js
ls -la frontend/src/components/SalesOrderList.js
ls -la frontend/src/components/AuditLogPanel.js
```

Expected: All three files exist

### 5.3 After Integration, Test

- Refresh frontend (Cmd+R)
- Role switcher should appear in header
- Approvals panel should show for managers
- Audit log should update in real-time

✅ Components integrated

---

## Section 6: End-to-End Demo Flow (15 min)

### 6.1 Operator Workflow

1. **Login as Operator**
   - Email: `operator@agenterp.com`
   - Password: `operator123`

2. **View Dashboard**
   - See chat interface ready
   - See pending sales orders

3. **Create Order via Chat**
   - Type: "Create a sales order for Global Tech Industries with 2 servers and 1 network switch"
   - Expected: Chat shows order creation confirmation
   - Order value should exceed ₹50K
   - Agent should flag for approval

4. **Check if shows in Pending Approvals**
   - Navigate to Approvals panel (if visible)
   - New order should appear

✅ Operator workflow complete

### 6.2 Manager Workflow

1. **Switch to Manager Role**
   - Use Role Switcher if available, or re-login
   - Email: `manager@agenterp.com`
   - Password: `manager123`

2. **View Pending Approvals**
   - Approvals panel should show 2-3 pending orders
   - Each showing: Customer, amount, reason for approval
   - Buttons: Approve / Reject

3. **Approve an Order**
   - Click "Approve" on SO-2024-00101
   - Expected: Status changes to "Approved"
   - Audit log should show approval action

4. **Check Audit Trail**
   - Audit Log panel should show:
     - Order creation by operator
     - Flagged for approval (system)
     - Approval by manager
   - Timestamps should be recent

✅ Manager workflow complete

### 6.3 Chat-Driven Workflow

1. **Query Approvals**
   ```
   User: "Show me pending approvals over ₹100,000"
   Agent: Lists matching orders with details
   ```

2. **Get Credit Info**
   ```
   User: "Check credit for Global Tech Industries"
   Agent: Shows credit limit, payment history, risk level
   ```

3. **Approve via Chat**
   ```
   User: "Approve SO-2024-00101"
   Agent: Confirms approval, updates status
   ```

4. **View Audit**
   ```
   User: "Show audit log for SO-2024-00101"
   Agent: Shows complete order lifecycle
   ```

✅ Chat-driven demo complete

---

## Section 7: Data Verification

### 7.1 Check Seeded Customers
```bash
# Expected: 6 customers seeded
curl -s http://localhost:8001/api/entity \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"action":"query","doctype":"Customer","limit":10}' | jq '.data | length'
```

Expected output: `6`

### 7.2 Check Sales Orders
```bash
# Expected: 6 orders, 3+ pending approval
curl -s http://localhost:8001/api/entity \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"action":"query","doctype":"Sales Order","limit":10}' | jq '.data'
```

Expected: Orders include:
- SO-2024-00101 (₹545K, pending)
- SO-2024-00102 (₹1.05M, pending)
- SO-2024-00104 (₹620K, pending)
- Plus 3 others (various statuses)

### 7.3 Check Approval Requests
```bash
# Check MongoDB directly if possible
# Or via API:
curl -s http://localhost:8001/api/approvals \
  -H "Authorization: Bearer $MANAGER_TOKEN" | jq '.data | length'
```

Expected: 2-3 approval requests

### 7.4 Check Chat History
```bash
# 3 chat sessions with realistic messages
curl -s http://localhost:8001/api/chat/sessions \
  -H "Authorization: Bearer $TOKEN" | jq '.data | length'
```

Expected: 3 sessions (operator, manager, admin)

### 7.5 Check Audit Logs
```bash
# 8+ audit entries showing complete workflow
curl -s http://localhost:8001/api/audit?limit=20 \
  -H "Authorization: Bearer $TOKEN" | jq '.data | length'
```

Expected: 8-10 entries with actions like:
- create_order
- request_approval
- approve_request
- query_data

✅ All data present and correct

---

## Section 8: Performance Benchmarks

### 8.1 Load Times

**Measure with:** `curl -w "Time: %{time_total}s\n"` or browser DevTools

| Endpoint | Expected Time | Actual Time |
|----------|---------------|-------------|
| GET /health | <100ms | ________ |
| POST /login | <200ms | ________ |
| GET /entity (10 orders) | <500ms | ________ |
| GET /audit (10 logs) | <200ms | ________ |
| POST /auth/seed-demo | <5s | ________ |
| Chat message | <2s | ________ |

### 8.2 Dashboard Metrics Load
- Dashboard should load < 1 second
- Approvals panel with 3 items < 500ms
- Audit log with 10 entries < 300ms

✅ Performance acceptable for demo

---

## Section 9: Reset & Re-Run

### Between Demo Runs:

```bash
# Option 1: Via API
curl -X POST http://localhost:8001/api/auth/reset-demo
curl -X POST http://localhost:8001/api/auth/seed-demo

# Option 2: Manual reset
# Kill backend, delete MongoDB data, restart
```

Expected: Fresh demo state with same consistent data

---

## Section 10: Troubleshooting Matrix

| Problem | Check | Solution |
|---------|-------|----------|
| Backend won't start | Port 8001 in use | `lsof -ti:8001 \| xargs kill -9` |
| Seed fails | MongoDB missing | Uses in-memory, data lost on restart |
| Chat not working | Auth token | Verify Bearer token in headers |
| Approvals empty | Role is not manager | Switch to manager@agenterp.com |
| Audit log empty | DB connection | Check MongoDB URL in env |
| Frontend blank | CORS issue | Check backend includes auth_router |
| Role switcher missing | Component not integrated | Add RoleSwitcher to DashboardView |

---

## Verification Checklist

- [ ] Backend starts on port 8001
- [ ] Health check returns healthy
- [ ] Demo seeds without errors
- [ ] All 4 users can login
- [ ] 6 orders visible in system
- [ ] 3+ orders pending approval
- [ ] Chat creates orders
- [ ] Manager can approve orders
- [ ] Audit log shows complete trail
- [ ] Frontend loads without errors
- [ ] Role switcher works (if integrated)
- [ ] Approvals panel shows orders (if integrated)
- [ ] Dashboard metrics display correctly
- [ ] Demo can be reset and re-run
- [ ] Performance meets benchmarks

**Total Items:** 15/15

---

## Sign-Off

**Date:** ___________

**Tested By:** ___________

**All Systems Go?** ☐ YES ☐ NO

If "NO": Document issues in Section 10 and troubleshoot

---

**Ready for hackathon presentation! 🚀**
