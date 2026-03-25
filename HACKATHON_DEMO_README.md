# AgentERP Microsoft AI Hackathon - Complete Demo Guide

## Executive Summary

**AgentERP** is an AI-powered ERP orchestration layer that demonstrates:
1. **Proactive Risk Management** - Auto-flag high-value orders (>₹50K)
2. **Intelligent Approval Workflows** - Chat-driven and UI-based approvals
3. **Complete Audit & Compliance** - Real-time activity tracking
4. **Enterprise RBAC** - Role-based visibility and permissions
5. **Seamless ERPNext Integration** - Real API calls with mock fallback

---

## 🚀 Quick Start (5 minutes)

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
PYTHONPATH=$(pwd):/path/to/venv/lib/python3.11/site-packages \
  uvicorn server:app --host 0.0.0.0 --port 8001
```

Wait for: `Application startup complete`

### 2. Seed Demo Data
```bash
curl -X POST http://localhost:8001/api/auth/seed-demo
```

Expected: 
- ✅ 4 demo users
- ✅ 6 customers
- ✅ 6 sales orders (2+ high-value)
- ✅ 3 chat sessions with realistic history
- ✅ 8+ audit log entries

### 3. Start Frontend
```bash
cd frontend
npm start
```

Browser opens to: `http://localhost:3000`

### 4. Login & Demo
**Default Users:**
- 👤 Operator: `operator@agenterp.com` / `operator123`
- 👤 Manager: `manager@agenterp.com` / `manager123`
- 👤 Admin: `admin@agenterp.com` / `admin123`
- 👤 Viewer: `viewer@agenterp.com` / `viewer123`

---

## 📖 Demo Scenario: "High-Value Order Recovery & Approval Automation"

### Phase 1: Operator Creates Orders
```
User: "Create sales order for Global Tech Industries with 2 servers, 
       1 network switch, and 3 support packages"

Agent response shows:
- Order created: SO-2024-00101
- Total: ₹545,000
- ⚠️ Flagged for approval (exceeds ₹50K threshold)
```

### Phase 2: System Flags for Approval
- Order automatically marked "pending_approval"
- Manager notified via dashboard
- Approvals panel shows 2-3 pending high-value orders
- Total pending value: ₹2,215,000

### Phase 3: Manager Reviews & Approves
```
User (Manager): "Show me pending approvals over ₹500K"

Agent: Lists all pending orders with:
- Customer name & credit info
- Order value & line items
- Risk assessment
- Approval buttons

User: "Approve SO-2024-00101 and SO-2024-00102"

Agent: Approves both orders, updates status, sends notifications
```

### Phase 4: Audit Trail & Compliance
- Audit log shows complete lifecycle:
  - Order created by operator
  - Flagged for approval (system)
  - Approved by manager with reasoning
- All timestamps and user info recorded
- Exportable for compliance

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│          React Frontend              │  ← Port 3000
│  (Chat, Dashboard, Approvals)        │
└─────────────┬───────────────────────┘
              │
              │ HTTP (Bearer Tokens)
              │
┌─────────────▼───────────────────────┐
│        FastAPI Backend               │  ← Port 8001
│  ┌─────────────────────────────────┐ │
│  │ Routes:                         │ │
│  │ - /auth       (login, register) │ │
│  │ - /chat       (sessions, msgs)  │ │
│  │ - /approvals  (RBAC, workflow)  │ │
│  │ - /audit      (compliance trail)│ │
│  │ - /entity     (generic CRUD)    │ │
│  │ - /erp        (customer, order) │ │
│  └─────────────────────────────────┘ │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼──────┐    ┌────────▼────┐
│ MongoDB  │    │  ERPNext    │
│(Persist) │    │(Integration)│
└──────────┘    └─────────────┘
```

**Data Flow:**
1. Frontend sends natural language queries
2. Backend parses and routes to appropriate service
3. Services interact with MongoDB (local state) & ERPNext (real ERP)
4. Agent generates contextual responses
5. All actions logged to audit trail
6. RBAC enforced at route level

---

## 📊 Demo Data at a Glance

### Customers (6)
- Acme Manufacturing
- Global Tech Industries  ← Featured in hero scenario
- Innovation Labs Inc
- Enterprise Solutions Ltd  ← Featured in hero scenario
- Cloud Systems Partners
- Data Analytics Corp

### Sales Orders (6)
| Order ID | Customer | Amount | Status | Notes |
|----------|----------|--------|--------|-------|
| SO-2024-00101 | Global Tech | ₹545K | Approved | High-value |
| SO-2024-00102 | Enterprise | ₹1,050K | Approved | CRITICAL high-value |
| SO-2024-00103 | Acme | ₹61K | Submitted | Normal |
| SO-2024-00104 | Data Analytics | ₹620K | Pending | High-value - waiting |
| SO-2024-00099 | Innovation Labs | ₹210K | In Delivery | Delayed old order |
| SO-2024-00095 | Cloud Systems | ₹50K | Completed | Success story |

**Key Metrics:**
- Total Sales: ₹2,536,000
- High-Value Orders: 4
- Pending Approvals: 1 (₹620K)
- Approval Rate: 67% → 100%

### Chat History (3 sessions)
**Session 1 - Operator Creates Orders**
- 4 messages showing order creation flow
- System auto-flagging high-value orders
- Real business context

**Session 2 - Manager Reviews & Approves**
- 6 messages showing approval workflow
- Credit assessment queries
- Approval decisions

**Session 3 - Executive Dashboard**
- Admin reviewing high-level metrics
- Performance summary
- Business impact

### Audit Logs (8+ entries)
1. Operator creates order SO-2024-00101
2. System flags for approval (high-value)
3. Operator creates order SO-2024-00102
4. System critical alert (very high-value)
5. Manager queries pending approvals
6. Manager approves SO-2024-00101
7. Manager approves SO-2024-00102
8. Admin accesses audit logs

---

## 🔑 Key Features Demonstrated

### 1. **Threshold-Based Auto-Flagging**
- Orders >₹50,000 auto-marked "pending_approval"
- No manual intervention needed
- AI proactively alerts management

### 2. **Multi-Channel Approvals**
- **Chat:** "Approve order SO-2024-00101"
- **UI:** Click "Approve" in Approvals panel
- **Admin:** Bulk operations via API
- All channels update in real-time

### 3. **Role-Based Access Control**
```
Admin (admin@agenterp.com):
  ✓ View all orders & approvals
  ✓ Approve/reject any order
  ✓ Access audit logs (complete)
  ✓ Manage users & roles
  ✓ System configuration

Manager (manager@agenterp.com):
  ✓ View pending approvals
  ✓ Approve/reject orders
  ✓ View audit logs (own department)
  ✓ View customers & orders

Operator (operator@agenterp.com):
  ✓ Create sales orders
  ✓ View own orders
  ✓ View basic audit trail
  ✗ Cannot approve

Viewer (viewer@agenterp.com):
  ✓ View all orders (read-only)
  ✗ Cannot create or approve
```

### 4. **Immutable Audit Trail**
- Every action logged with:
  - User ID & email & role
  - Action type (create, approve, etc.)
  - Resource type & ID
  - Timestamp (ISO 8601)
  - Result (success/failure)
  - Context & reasoning
- Useful for: compliance, debugging, analytics

### 5. **Chat-Driven Operations**
Try these in chat:
```
# Queries
"Show me pending approvals"
"Which orders are delayed?"
"What's our total sales value this week?"
"Show audit log for SO-2024-00101"

# Actions
"Create order for [customer] with [items]"
"Approve order SO-2024-00101"
"Reject SO-2024-00104 - customer credit issues"

# Analysis
"Check credit for Global Tech Industries"
"Why is SO-2024-00099 delayed?"
"Show me high-value orders this month"
```

---

## 🔧 Technical Details

### Backend Tech Stack
- **Framework:** FastAPI (async, modern)
- **Database:** MongoDB (with in-memory fallback)
- **Auth:** JWT tokens + bcrypt
- **Validation:** Pydantic models
- **ERP Integration:** httpx (async HTTP client)
- **Monitoring:** Logging module

### Frontend Tech Stack
- **Framework:** React 18
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State:** Context API
- **Components:** Custom (no heavy dependencies)

### Database Schema
```
users:
  - id, email, password_hash, name, role, created_at, last_login

chat_sessions:
  - id, user_id, user_email, created_at, updated_at, title

chat_messages:
  - id, session_id, role (user/assistant), content, timestamp

sales_orders:
  - id, order_id, customer, items[], grand_total, status, approval_status

approval_requests:
  - id, order_id, customer, amount, status, requester_id, approver_id

audit_logs:
  - id, user_id, user_email, user_role, action, resource_type, 
    resource_id, timestamp, result, result_message
```

---

## 🎯 Demo Scripts

### Script 1: Basic Demo (5 min)
1. Login as operator
2. Create one high-value order
3. Watch system flag it
4. Switch to manager
5. Approve the order
6. Show audit trail

**Goals:** Threshold flagging + RBAC + Audit trail

### Script 2: Full Workflow (10 min)
1. Start with data already seeded
2. Show dashboard with metrics
3. Review pending approvals
4. Demonstrate chat-driven approvals
5. Show complete audit trail
6. Discuss compliance & risk management

**Goals:** End-to-end workflow, intelligence, compliance

### Script 3: Business Impact (15 min)
1. Walk through hero scenario step-by-step
2. Show all 3 orders with different scenarios
3. Discuss credit assessment in chat
4. Demonstrate multi-channel approval
5. Show dashboard impact
6. Discuss ROI: time saved, risk reduced, visibility

**Goals:** Complete business narrative, ROI, enterprise-readiness

---

## 📈 Demo Talking Points

### Point 1: Proactivity
> "Traditional ERP requires manual review queues. AgentERP proactively identifies high-value orders and flags them immediately. No order slips through."

**Demo:** Show SO-2024-00101 auto-flagged within seconds of creation.

### Point 2: Visibility
> "Managers get complete context in their approval interface—customer credit history, payment patterns, risk assessment. Data-driven approval decisions."

**Demo:** Query "Check credit for Global Tech Industries" and show intelligent response.

### Point 3: Flexibility
> "Approve via chat, via dashboard, via API. One system, multiple interfaces. Teams work how they want."

**Demo:** Approve SO-2024-00101 via chat, SO-2024-00102 via UI panel.

### Point 4: Compliance
> "100% audit trail. Every action logged with who, what, when, why. Minutes to export compliance reports."

**Demo:** Show audit log has 8+ entries covering entire lifecycle.

### Point 5: Intelligence
> "AI learns business rules (₹50K threshold) and applies them consistently. Reduces manual rule enforcement."

**Demo:** Create order for ₹49K (not flagged), ₹100K (flagged). Show consistency.

---

## 🔄 Reset & Replay

To demonstrate the scenario multiple times:

### Option 1: Via API
```bash
# Reset (clear all data)
curl -X POST http://localhost:8001/api/auth/reset-demo

# Re-seed (reload demo scenario)
curl -X POST http://localhost:8001/api/auth/seed-demo

# Then refresh frontend (F5)
```

### Option 2: Restart Backend
```bash
# Just restart the server (if using in-memory DB)
# Ctrl+C in backend terminal
# Then re-start
uvicorn server:app --host 0.0.0.0 --port 8001

# MongoDB data persists, needs manual reset
```

---

## ✅ Verification Checklist

Before demo:
- [ ] Backend runs on port 8001
- [ ] Seed completes without errors
- [ ] All 4 users can login
- [ ] Operator can create order
- [ ] Manager can see approvals
- [ ] Audit logs show actions
- [ ] Chat responds in <2 sec
- [ ] Dashboard loads <1 sec
- [ ] No console errors (F12)

---

## 📚 Additional Documentation

- **HACKATHON_DEMO_SCENARIO.md** - Detailed step-by-step walkthrough
- **DEMO_VERIFICATION_CHECKLIST.md** - Complete verification guide
- **DEMO_QUICK_START.sh** - Automated setup script
- **API_DOCUMENTATION.md** - API reference (if present)

---

## 🚨 Troubleshooting Quick Reference

| Issue | Fix |
|-------|-----|
| Backend won't start | `lsof -ti:8001 \| xargs kill -9` then restart |
| Seed fails | Check MongoDB running or use in-memory |
| Login doesn't work | Verify users seeded: `curl localhost:8001/api/auth/users` |
| Approvals empty | Login as manager not operator |
| Chat broken | Check backend logs for errors |
| Audit log empty | Refresh page or check MongoDB connection |
| Components missing | May need integration into DashboardView |

---

## 🎤 Presenter Notes

**Opening (1 min):**
"AgentERP brings AI-powered intelligence to ERP operations. Today we're demonstrating how it prevents costly approval delays by proactively managing high-value orders across your entire organization."

**Problem Statement (1 min):**
"In traditional ERP systems, high-value orders get stuck in approval queues. Managers lack context. Audit trails are manual. This costs time and introduces risk."

**Solution (2 min):**
"AgentERP solves this with three key capabilities:
1. **Proactive flagging** - meets orders automatically identified
2. **Intelligent approvals** - managers get full context in seconds
3. **Immutable audit** - complete compliance trail"

**Demo (10-15 min):**
[Walk through hero scenario]

**Impact (2 min):**
"With AgentERP:
- High-value orders approved in <24 hours (vs 2-3 days)
- 100% compliance audit trail (zero manual entry)
- Managers make data-driven decisions (credit checks, risk assessment)
- System scales to millions in transaction value"

**Close (1 min):**
"AgentERP makes ERPNext smarter, not harder. One query, complete visibility."

---

## 📞 Support

For issues or questions:
1. Check DEMO_VERIFICATION_CHECKLIST.md
2. Review backend logs (terminal where uvicorn runs)
3. Check browser console (F12)
4. Verify endpoints with curl
5. Reset demo data and re-seed

---

**Last Updated:** 2024-01-15  
**Status:** ✅ Ready for Hackathon  
**Demo Duration:** 5-15 minutes (depending on depth)

🚀 **Let's impress the judges!**
