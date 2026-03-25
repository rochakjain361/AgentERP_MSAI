# 🎯 AgentERP Management Demo - Complete Setup Guide

## ✅ What's Implemented

### Backend (FastAPI + MongoDB)

#### 1. **Role-Based Access Control (RBAC)**
- ✓ 4 Demo User Roles:
  - `admin@agenterp.com` → Full system access
  - `manager@agenterp.com` → Approve high-value orders
  - `operator@agenterp.com` → Create orders, operators can't delete
  - `viewer@agenterp.com` → Read-only access

#### 2. **Approval Workflow**
- ✓ Auto-trigger approval for orders > ₹50,000
- ✓ Manager review queue at `/api/approvals`
- ✓ Approve/Reject with audit trail
- ✓ Collections: `approval_requests`

#### 3. **Audit Logging**
- ✓ Tracks: user_id, role, action, resource, timestamp, result
- ✓ Endpoints: 
  - `GET /api/audit` - Get logs with filtering
  - `GET /api/audit/recent` - Recent activity
- ✓ Collection: `audit_logs`

#### 4. **Demo Data Seeding**
- ✓ Seed script: `backend/seed_demo_data.py`
- ✓ Seeds:
  - 4 demo users
  - 4 customers (Acme, Global Tech, Innovation Labs, Enterprise Solutions)
  - 5-6 sales orders (2+ high-value pending approval)
  - Audit logs for demo

### Frontend (React)

#### 1. **Role Switcher Component**
- ✓ Location: `src/components/RoleSwitcher.js`
- ✓ Quick switch between roles
- ✓ Display user permissions

#### 2. **Sales Order Panel**
- ✓ Location: `src/components/SalesOrderList.js`
- ✓ Managers see pending approvals
- ✓ Approve/Reject buttons with confirmation
- ✓ Order details with amounts

#### 3. **Audit Log Panel**
- ✓ Location: `src/components/AuditLogPanel.js`
- ✓ Filter by action type
- ✓ Shows user, action, result, timestamp
- ✓ Real-time updates

### API Endpoints

#### Authentication
```
POST /api/auth/login              - Login user
POST /api/auth/register            - Register new user
POST /api/auth/seed                - Seed default users
POST /api/auth/seed-demo           - Seed full demo data
GET  /api/auth/verify              - Verify token
GET  /api/auth/me                  - Get current user
```

#### Approvals
```
GET  /api/approvals                - Get pending approvals (manager/admin)
GET  /api/approvals/my-requests    - Get my approval requests
GET  /api/approvals/{id}           - Get approval details
POST /api/approvals/{id}/decide    - Approve/Reject
```

#### Audit Logs
```
GET  /api/audit                    - Get audit logs with filters
GET  /api/audit/recent             - Get recent activity
GET  /api/audit/summary/{user_id}  - Get user summary
GET  /api/audit/stats              - Get audit statistics
```

### Database Collections

```
users                    - User accounts with roles
customers               - Customer master data
sales_orders           - Sales orders with approval status
approval_requests      - Approval workflow tracking
audit_logs             - Complete audit trail
```

---

## 🚀 Quick Start

### 1. Seed Demo Data

**Option A: Via API (Easy)**
```bash
# Start backend first (see below)
curl -X POST http://localhost:8001/api/auth/seed-demo
```

**Option B: Via Script**
```bash
cd backend
python3 seed_demo_data.py
```

### 2. Start Backend
```bash
cd backend
PYTHONPATH=./venv/lib/python3.11/site-packages:. \
  ./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
```

### 3. Start Frontend
```bash
cd frontend
npm start
# Opens http://localhost:3000
```

---

## 🔐 Demo Credentials

| User | Email | Password | Role | Permissions |
|------|-------|----------|------|------------|
| SYSTEM ADMIN | admin@agenterp.com | admin123 | admin | Full access, all companies |
| APPROVAL MGR | manager@agenterp.com | manager123 | manager | Review & approve orders |
| ORDER CREATOR | operator@agenterp.com | operator123 | operator | Create orders, view data |
| VIEWER | viewer@agenterp.com | viewer123 | viewer | Read-only access |

---

## 📊 Demo Scenario Walkthrough

### 👤 **1. Operator Creates High-Value Order**
```
1. Login as: operator@agenterp.com / operator123
2. Create new Sales Order for "Acme Corporation"
3. Add items > ₹50,000 (e.g., 10x Enterprise License @ ₹5000 = ₹50,000)
4. System flags: "Pending Approval" (high value detected)
5. Audit log: CREATE_ORDER [pending status]
```

### ✅ **2. Manager Reviews & Approves**
```
1. Login as: manager@agenterp.com / manager123
2. See "Approval Queue" showing 1 pending order
3. Review customer, amount, items
4. Click "Approve" button
5. Order status changes to "approved"
6. Audit log: APPROVE_REQUEST [by manager]
```

### 📋 **3. Check Audit Trail**
```
1. Switch to any user
2. Go to "Audit Log" panel
3. See complete history:
   - Operator created order
   - Manager approved order
   - All timestamps and details
```

### 🚫 **4. Viewer Can Only Read**
```
1. Login as: viewer@agenterp.com / viewer123
2. Can view orders, audit logs
3. Cannot create or approve
4. Button disabled with reason
```

---

## 🔧 Integration with Existing Components

### Adding To Dashboard

**DashboardView.js** should include:

```jsx
import RoleSwitcher from './RoleSwitcher';
import SalesOrderList from './SalesOrderList';
import AuditLogPanel from './AuditLogPanel';

// In header
<RoleSwitcher 
  currentUser={user}
  onRoleSwitch={handleRoleSwitch}
  onLogout={logout}
/>

// In main content
<div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
  <SalesOrderList user={user} />
  <AuditLogPanel user={user} />
</div>
```

### AuthContext Extensions

Already supports:
- ✓ `login(email, password)`
- ✓ `logout()`
- ✓ `register(email, password, name, role, company)`

Add role switching:
```jsx
const switchRole = async (email, password) => {
  const result = await login(email, password);
  return result;
};
```

---

## 🎯 Access Control Rules

### By Role

**ADMIN** (Full Access)
- ✓ Create/edit/delete any data
- ✓ Approve all requests
- ✓ See all companies
- ✓ Manage users

**MANAGER** (Approve + Edit)
- ✓ Review & approve orders > ₹50K
- ✓ Edit own company data
- ✓ View company audit logs
- ✗ Cannot delete records
- ✗ Cannot manage users

**OPERATOR** (Create + View)
- ✓ Create orders for own company
- ✓ View own company data
- ✓ View own audit logs
- ✗ Cannot edit other orders
- ✗ Cannot delete
- ✗ Cannot approve

**VIEWER** (Read-Only)
- ✓ View orders
- ✓ View customers
- ✓ View audit logs
- ✗ Cannot create
- ✗ Cannot edit
- ✗ Cannot delete

---

## 📊 High-Value Approval Rules

**Threshold: ₹50,000**

Triggers approval when:
- Sales Order `grand_total` > ₹50,000
- Created by: operator/manager
- Requires approval by: manager/admin
- Status: `pending_approval`

**Approval Flow:**
1. Order created → Automatically flagged
2. Manager views in "Approval Queue"
3. Manager reviews details
4. Manager: Approve → Order executes
5. Manager: Reject → Order cancelled

Audit logs every step ✓

---

## 🧪 Testing Checklist

- [ ] Login with each role works
- [ ] Demo users auto-created on first seed
- [ ] Operator can create high-value orders
- [ ] Orders > ₹50K show as `pending_approval`
- [ ] Manager sees pending in queue
- [ ] Manager can approve/reject
- [ ] Audit log shows all actions
- [ ] Viewer cannot create (button disabled)
- [ ] Viewer sees read-only data
- [ ] Role switcher in header
- [ ] Approval panel only visible to manager/admin
- [ ] Audit log filters work

---

## 🔍 Debugging

### Check MongoDB Data
```bash
# In MongoDB shell
db.users.find().pretty()
db.sales_orders.find().pretty()
db.approval_requests.find().pretty()
db.audit_logs.find().pretty()
```

### Check Logs
```bash
# Backend logs
tail -f backend/server.log

# Frontend console
Open DevTools → Console tab
```

### Verify Seeding
```bash
curl http://localhost:8001/api/auth/seed-demo
# Should return: { "status": "success", ... }
```

---

## 📚 Files Modified/Created

### Backend
- ✓ `backend/seed_demo_data.py` - **NEW** comprehensive seeding
- ✓ `backend/services/auth_service.py` - Updated seed_default_users
- ✓ `backend/routes/auth.py` - Added /seed-demo endpoint
- ✓ `backend/server.py` - Registered auth router
- ✓ `backend/database.py` - Added users collection to MockDB

### Frontend
- ✓ `frontend/src/components/RoleSwitcher.js` - **NEW**
- ✓ `frontend/src/components/SalesOrderList.js` - **NEW** (approval panel)
- ✓ `frontend/src/components/AuditLogPanel.js` - **NEW**
- ✓ `frontend/src/components/LoginModal.js` - Updated demo user emails
- ✓ `frontend/.env` - Already configured (port 8001)

---

## ✨ What's Demo-Ready

✅ Complete RBAC system
✅ Approval workflow (high-value detection)
✅ Audit trail (full activity log)
✅ Seed data (users, customers, orders)
✅ Frontend UI (role switcher, approval panel, audit log)
✅ API endpoints (authentication, approvals, audit)
✅ Database collections (all required schemas)

---

## 🎬 Next Steps

1. **Start Backend**: `cd backend && ./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001`
2. **Seed Data**: `curl -X POST http://localhost:8001/api/auth/seed-demo`
3. **Start Frontend**: `cd frontend && npm start`
4. **Open Browser**: http://localhost:3000
5. **Login as Operator**: Click "Operator" quick login button
6. **Try Demo**: Create an order OR view existing pending approvals
7. **Switch Role**: Click RoleSwitcher to try Manager/Admin/Viewer roles

---

## 🎯 Demo Flow (Complete)

```
┌─────────────────────────────────────────┐
│  Frontend: Login Screen                 │
│  Quick buttons: Admin, Manager,         │
│                 Operator, Viewer        │
└──────────────┬──────────────────────────┘
               │ Click "Operator"
               ▼
┌─────────────────────────────────────────┐
│  Frontend: Dashboard (Operator View)    │
│  - Create Order button                  │
│  - Audit Log (read-only)                │
│  - RoleSwitcher in header               │
└──────────────┬──────────────────────────┘
               │ Create Order > ₹50K
               ▼
┌─────────────────────────────────────────┐
│  Backend: Approval Service              │
│  - Detects high value                   │
│  - Creates approval_requests doc        │
│  - Logs to audit_logs                   │
└──────────────┬──────────────────────────┘
               │ Auto-flags as pending
               ▼
┌─────────────────────────────────────────┐
│  Frontend: RoleSwitcher                 │
│  Switch to "Manager"                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Frontend: Dashboard (Manager View)     │
│ ╔─ Approval Queue ──────────────────╗  │
│ ║ 1 pending order from Operator     ║  │
│ ║ Customer: Acme                    ║  │
│ ║ Amount: ₹60,000 >> [APPROVE] [X] ║  │
│ ╚───────────────────────────────────╝  │
└──────────────┬──────────────────────────┘
               │ Click APPROVE
               ▼
┌─────────────────────────────────────────┐
│  Backend: Approval Service              │
│  - Update approval_requests to approved │
│  - Update sales_orders to approved      │
│  - Log to audit_logs                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Frontend: Audit Log                    │
│  Shows complete trace:                  │
│  1. operator@... CREATE_ORDER [pending] │
│  2. manager@... APPROVE_REQUEST [✓]     │
│  Timestamps, user roles, all details    │
└─────────────────────────────────────────┘
```

---

## 🎨 UI Components Summary

| Component | File | Purpose |
|-----------|------|---------|
| RoleSwitcher | RoleSwitcher.js | Switch demo user roles |
| SalesOrderList | SalesOrderList.js | Show pending approvals |
| AuditLogPanel | AuditLogPanel.js | Display activity logs |
| LoginModal | LoginModal.js | Login with quick role buttons |

---

**System Ready for Demo! 🚀**
