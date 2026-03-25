# 🚀 Quick Reference - Management Demo Testing

## 🔗 API Endpoints Quick Test

### Check Server Running
```bash
curl http://localhost:8001/api/health
# Expected: 200 OK
```

### Seed Demo Data
```bash
curl -X POST http://localhost:8001/api/auth/seed-demo
# Expected: { "status": "success", "summary": {...} }
```

### Login as Operator
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@agenterp.com","password":"operator123"}'
# Copy the access_token from response
```

### Get Pending Approvals (use token from above)
```bash
curl -H "Authorization: Bearer {TOKEN}" \
  http://localhost:8001/api/approvals
# Expected: array of pending orders
```

### Get Audit Logs
```bash
curl -H "Authorization: Bearer {TOKEN}" \
  http://localhost:8001/api/audit?limit=10
# Expected: audit log entries
```

---

## 🎭 Demo User Quick Logins

| Role | Email | Password | Access |
|------|--------|----------|--------|
| 👨‍💼 ADMIN | admin@agenterp.com | admin123 | Everything |
| 👔 MANAGER | manager@agenterp.com | manager123 | Approvals |
| 👷 OPERATOR | operator@agenterp.com | operator123 | Create Orders |
| 👁️ VIEWER | viewer@agenterp.com | viewer123 | Read Only |

---

## 📊 Orders in Demo Data

| Customer | Amount | Status | Needs Approval | Notes |
|----------|--------|--------|---|---|
| Acme | ₹60,000 | Pending | ✅ YES | High value |
| Global Tech | ₹95,000 | Pending | ✅ YES | High value |
| Innovation Labs | ₹15,000 | Completed | ❌ NO | Normal |
| Enterprise | ₹20,000 | Completed | ❌ NO | Normal |
| Acme | ₹55,000 | Approved | ✅ WAS | Already approved |

**Threshold: ₹50,000** - Orders above this need manager approval

---

## 🧪 Test Scenarios (Copy-Paste)

### Test 1: Login & Role Switch
```
1. Open http://localhost:3000
2. Click "Operator" button (quick login)
3. See dashboard with RoleSwitcher in header
4. Click RoleSwitcher dropdown
5. Select "Manager"
6. Page reloads as manager
7. See "Approval Queue" panel
```

### Test 2: Manager Approves Order
```
1. Logged in as Manager (from Test 1)
2. Look for "Approval Queue" or "Sales Orders" panel
3. Click on first pending order (₹60,000)
4. Click "Approve" button
5. Order status changes to "approved"
6. Confirmation message appears
```

### Test 3: Check Audit Log
```
1. From any logged-in view
2. Look for "Audit Log" panel (right side)
3. See entries like:
   - operator@... CREATE_ORDER [pending]
   - manager@... APPROVE_REQUEST [success]
4. Click filter tabs: "All", "Logins", "Orders Created", "Approvals"
5. Logs update based on filter
```

### Test 4: Viewer Has No Permission
```
1. Click RoleSwitcher → Switch to Viewer
2. Approval Queue panel DISAPPEARS (read-only only)
3. Audit Log still visible (can view)
4. Cannot create/edit anything
5. Try accessing /api/approvals - returns 403
```

### Test 5: Create New User & Login
```
1. Go to login form
2. Switch to "Sign Up" tab
3. Fill in:
   - Email: newuser@test.com
   - Password: password123
   - Name: Test User
   - Role: Operator
   - Company: TechCorp Solutions
4. Click "Create Account"
5. Auto-logged in
6. New user in database with audit log
```

---

## 📱 Component Locations in UI

```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
│  AgentERP Dashboard         [RoleSwitcher]  │ ← Role switching
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────┐  ┌────────────────┐  │
│  │                 │  │                │  │
│  │ Sales Orders    │  │  Audit Log     │  │
│  │ (Approvals)     │  │  (Activity)    │  │
│  │                 │  │                │  │
│  │ - Pending items │  │ - User actions │  │
│  │ - Amount        │  │ - Timestamps   │  │
│  │ - Approve btn   │  │ - Filters      │  │
│  │                 │  │                │  │
│  └─────────────────┘  └────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │ Additional KPI Cards or Info        │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- [ ] Backend running on port 8001? `lsof -i :8001`
- [ ] Frontend .env points to port 8001?
- [ ] CORS enabled in FastAPI? (should be)

### "No pending orders showing"
- [ ] Seeded demo data? `curl -X POST http://localhost:8001/api/auth/seed-demo`
- [ ] Logged in as manager? (only managers see approvals)
- [ ] Check browser console for API errors

### "Role switcher not appearing"
- [ ] Logged in? Shows only for authenticated users
- [ ] Check if `user` data is populated
- [ ] See browser console for JS errors

### "Audit log empty"
- [ ] Data seeded?
- [ ] Performed actions after seeding? (logins, orders)
- [ ] Check API response: `curl http://localhost:8001/api/audit`

### "Approve button disabled"
- [ ] Logged in as manager/admin?
- [ ] Approval in "pending" status?
- [ ] Check browser console for errors

---

## 📊 Expected API Responses

### GET /api/approvals (Manager)
```json
{
  "status": "success",
  "approvals": [
    {
      "id": "...",
      "order_id": "...",
      "requester_email": "operator@agenterp.com",
      "resource_data": {
        "customer": "Acme",
        "grand_total": 60000,
        "items": [...]
      },
      "status": "pending",
      "reason": "Order value ₹60,000 exceeds threshold",
      "requested_at": "2026-03-25T..."
    }
  ]
}
```

### GET /api/audit
```json
{
  "status": "success",
  "logs": [
    {
      "id": "...",
      "user_email": "operator@agenterp.com",
      "user_role": "operator",
      "action": "create_order",
      "resource_type": "Sales Order",
      "result": "pending",
      "timestamp": "2026-03-25T...",
      "approval_required": true
    }
  ]
}
```

---

## ✅ Verification Checklist

### Before Demo
- [ ] Backend running: `curl http://localhost:8001/api/health`
- [ ] Data seeded: `curl -X POST http://localhost:8001/api/auth/seed-demo`
- [ ] Frontend running: `npm start` in frontend folder
- [ ] Can login as operator
- [ ] Can see RoleSwitcher
- [ ] Can see pending orders (manager)
- [ ] Can see audit logs

### During Demo
- [ ] Operator creates → shows pending
- [ ] Switch to manager → see queue
- [ ] Approve order → status changes
- [ ] Audit log updated
- [ ] View can't approve → button disabled

### After Demo
- [ ] Approvers can repeat flow
- [ ] New users can register
- [ ] Data persists in MongoDB (or in-memory)
- [ ] All audit logs recorded

---

## 🎯 Common Commands

```bash
# Backend
cd backend
./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001

# Seed data
curl -X POST http://localhost:8001/api/auth/seed-demo

# Frontend
cd frontend
npm start

# Check MongoDB (if available)
mongo
> use agenterp
> db.users.find()
> db.approval_requests.find()
> db.audit_logs.find()
```

---

## 📚 File References

| Component | File | Purpose |
|-----------|------|---------|
| Header | N/A | Add RoleSwitcher import |
| Role Switcher | RoleSwitcher.js | Switch between roles |
| Approvals | SalesOrderList.js | Manager approval panel |
| Audit Log | AuditLogPanel.js | Activity log display |
| Login | LoginModal.js | Demo user quick buttons |
| Routing | n/a | No new routes needed |

---

**Start testing now! 🚀**
