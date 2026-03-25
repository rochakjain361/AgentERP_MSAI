# Microsoft AI Hackathon Demo Scenario

## Hero Narrative: "High-Value Order Recovery & Approval Automation"

**Goal:** Demonstrate AgentERP's ability to proactively manage high-value orders, flag them for approval, and maintain complete visibility through AI-powered chat, approval workflows, and audit trails.

---

## Quick Setup (5 minutes)

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
PYTHONPATH=/path/to/backend:/path/to/backend/venv/lib/python3.11/site-packages \
  uvicorn server:app --host 0.0.0.0 --port 8001

# Terminal 2: Seed Demo Data
curl -X POST http://localhost:8001/api/auth/seed-demo

# Terminal 3: Frontend
cd frontend
npm start

# Open browser to http://localhost:3000
```

---

## Demo Scenario Flow (15 minutes)

### Phase 1: Operator Creates Orders (3 min)

**Actor:** Raj Patel (Operator)  
**Goal:** Create sales orders for clients

1. **LOGIN**
   - Email: `operator@agenterp.com`
   - Password: `operator123`
   - Expected: Dashboard opens with empty chat

2. **CHAT INTERACTION 1**
   ```
   User: "Create a sales order for Global Tech Industries with 2 enterprise servers, 
           1 network switch, and 3 support packages"
   ```
   
   Expected response:
   ```
   📋 I've created sales order SO-2024-00101 for Global Tech Industries.
   
   Order Details:
   - 2x Enterprise Server - 64GB RAM @ ₹150,000 = ₹300,000
   - 1x Network Switch - 48 Port @ ₹85,000 = ₹85,000
   - 3x Premium Support Package @ ₹25,000 = ₹75,000
   
   Total: ₹545,000
   
   ⚠️ IMPORTANT: This order exceeds the ₹50,000 approval threshold 
   and requires manager approval.
   ```
   
   **Why this matters:**
   - Order is HIGH-VALUE (₹545K > ₹50K threshold)
   - System AUTOMATICALLY flags for approval
   - Agent provides immediate visibility to risk

3. **CHAT INTERACTION 2**
   ```
   User: "Now create an order for Enterprise Solutions Ltd - 
           20 licenses and 5 days of training"
   ```
   
   Expected response:
   ```
   ✅ I've created sales order SO-2024-00102 for Enterprise Solutions Ltd.
   
   Order Details:
   - 20x Enterprise Software License @ ₹50,000 = ₹1,000,000
   - 5x Training Services @ ₹10,000 = ₹50,000
   
   Total: ₹1,050,000
   
   🔴 CRITICAL: This is a very high-value order (₹1,050,000). 
   It requires immediate manager approval. System has auto-flagged for 
   management review.
   ```
   
   **Why this matters:**
   - Order is VERY HIGH-VALUE (₹1.05M)
   - Demonstrates proactive risk flagging
   - Chat shows realistic business context

---

### Phase 2: Manager Reviews & Approves (5 min)

**Actor:** Sarah Johnson (Manager)  
**Goal:** Review high-value orders and make approval decisions

1. **SWITCH ROLE**
   - Click "Manager" button in role switcher (if integrated)
   - Or logout and login as manager:
     - Email: `manager@agenterp.com`
     - Password: `manager123`

2. **VIEW PENDING APPROVALS PANEL**
   - Expected: "Sales Order List" or "Approvals Panel" shows:
     ```
     📊 Pending Approvals (3)
     
     ┌─────────────────────────────────────────────────────┐
     │ SO-2024-00101 - Global Tech Industries              │
     │ Amount: ₹545,000                                    │
     │ Reason: High-value order (>₹50,000 threshold)      │
     │ [Approve] [Reject]                                  │
     ├─────────────────────────────────────────────────────┤
     │ SO-2024-00102 - Enterprise Solutions Ltd            │
     │ Amount: ₹1,050,000                                 │
     │ Reason: CRITICAL - Very high-value order           │
     │ [Approve] [Reject]                                  │
     ├─────────────────────────────────────────────────────┤
     │ SO-2024-00104 - Data Analytics Corp                │
     │ Amount: ₹620,000                                    │
     │ Reason: High-value order (>₹50,000 threshold)      │
     │ [Approve] [Reject]                                  │
     └─────────────────────────────────────────────────────┘
     ```

3. **CHAT INTERACTION 1**
   ```
   User: "Show me pending approvals above ₹50,000"
   ```
   
   Expected: Agent lists all 3 pending high-value orders with:
   - Order ID and customer name
   - Amount and line items
   - Risk assessment
   - Total pending value: ₹2,215,000

4. **CHAT INTERACTION 2** (Due Diligence)
   ```
   User: "Check credit history for Global Tech Industries - 
          are they reliable?"
   ```
   
   Expected:
   ```
   ✅ Credit Assessment for Global Tech Industries
   
   - Credit Limit: ₹1,500,000
   - Current Outstanding: ₹0
   - Payment History: Excellent (on-time payments for 8+ orders)
   - Account Age: 18 months
   - Risk Level: LOW ✓
   
   Recommendation: Safe to approve. Customer has demonstrated 
   reliability and adequate credit capacity.
   ```

5. **APPROVE ORDERS**
   ```
   User: "Approve SO-2024-00101 and SO-2024-00102"
   ```
   
   Expected:
   ```
   ✅ Approvals Processed
   
   ✓ SO-2024-00101 (Global Tech Industries - ₹545,000)
     - Status changed from Pending to Approved
     - Approved by: Sarah Johnson (manager@agenterp.com)
     - Timestamp: 2024-01-03 10:45 AM
   
   ✓ SO-2024-00102 (Enterprise Solutions Ltd - ₹1,050,000)
     - Status changed from Pending to Approved
     - Approved by: Sarah Johnson (manager@agenterp.com)
     - Timestamp: 2024-01-03 10:46 AM
     - Note: High-value order approved based on positive credit profile
   
   Total Approved Today: ₹1,595,000
   
   📧 Notifications sent to operator and sales teams.
   ```
   
   **Dashboard Impact:** Panel updates in real-time showing:
   - Remaining pending: 1 order (₹620K)
   - Approved this week: 2 orders (₹1.595M)
   - Approval rate: 67%

---

### Phase 3: Audit & Compliance Visibility (4 min)

**Actor:** Admin or Manager  
**Goal:** Demonstrate complete audit trail and compliance capability

1. **AUDIT LOG PANEL**
   Expected to see timestamped entries:
   ```
   📊 Activity Log (Real-time)
   
   14:45 UTC | Raj Patel (Operator)
   ✏️ Created Order SO-2024-00101
   Customer: Global Tech Industries | Amount: ₹545,000
   
   14:46 UTC | System
   🚩 Flagged for Approval
   Order SO-2024-00101 exceeds ₹50K threshold
   
   14:51 UTC | Raj Patel (Operator)
   ✏️ Created Order SO-2024-00102
   Customer: Enterprise Solutions Ltd | Amount: ₹1,050,000
   
   14:52 UTC | System  
   🚩 CRITICAL ALERT
   Order SO-2024-00102 very high value - immediate review needed
   
   15:30 UTC | Sarah Johnson (Manager)
   👁️ Reviewed Pending Approvals
   Query: pending_approvals > 50000
   
   15:45 UTC | Sarah Johnson (Manager)
   ✅ Approved Order SO-2024-00101
   Decision: APPROVED | Reason: Excellent credit history
   
   15:46 UTC | Sarah Johnson (Manager)
   ✅ Approved Order SO-2024-00102
   Decision: APPROVED | Reason: Strong customer relationship
   ```

2. **CHAT QUERY**
   ```
   User: "Show audit log for order SO-2024-00101"
   ```
   
   Expected: Agent shows complete order lifecycle:
   - Created by: operator@agenterp.com
   - Created at: 2024-01-02 14:46 UTC
   - Flagged for approval: automatic (high-value > ₹50K)
   - Approved by: manager@agenterp.com
   - Approved at: 2024-01-03 15:45 UTC
   - Approval reason: Excellent credit history

---

### Phase 4: Dashboard Metrics (2 min)

**Actor:** Any user  
**Expected Dashboard to show:**

```
📈 Business Metrics Dashboard

This Week Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Orders:           6
High-Value Orders:      4
Already Approved:       2 (₹1,595,000)
Still Pending:         1 (₹620,000)
Total Sales Pipeline:  ₹2,215,000

Status Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Approved:           2 orders
⏳ Pending:            1 order
📦 In Delivery:        1 order
✓ Completed:           1 order
📋 Draft:              1 order

Performance Metrics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average approval time:  < 24 hours
Approval success rate:  67% → 100%
Revenue from high-value: ₹2,215,000
Risk level:            All approved orders = LOW ✓
```

---

## Key Demo Talking Points

### 1. **Proactive Risk Management**
- ✅ Orders >₹50K automatically flagged
- ✅ Chat instantly alerts when risk detected
- ✅ No manual approval processes needed

### 2. **Complete Visibility**
- ✅ Managers see full order context in one view
- ✅ Credit assessment info available in chat
- ✅ Real-time audit trail shows every action

### 3. **Workflow Automation**
- ✅ Approvals can be done via chat or UI panel
- ✅ Status updates propagate to all views
- ✅ Audit logs auto-generated for compliance

### 4. **Enterprise-Ready**
- ✅ RBAC enforced (operator, manager, admin)
- ✅ Chat history persisted across sessions
- ✅ Deterministic demo data for repeatability
- ✅ ERPNext integration ready

### 5. **AI-Powered Intelligence**
- ✅ Natural language order creation ("create order for...")
- ✅ Smart flagging (threshold-based)
- ✅ Credit analysis in chat
- ✅ Contextual recommendations

---

## Reset Demo Between Runs

If you need to clear and re-seed demo data:

```bash
# Option 1: Via curl
curl -X POST http://localhost:8001/api/auth/reset-demo
curl -X POST http://localhost:8001/api/auth/seed-demo

# Option 2: Via admin endpoint in UI
# (If integrated) Click "Reset Demo" → "Seed Demo Data"
```

---

## Troubleshooting

### Backend won't start
```bash
# Ensure venv is activated and port 8001 is free
lsof -ti:8001 | xargs kill -9
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Seed endpoint fails
```bash
# Check backend logs for: "🚀 Starting Microsoft AI Hackathon demo seeding..."
# If MongoDB not available, will use in-memory (data lost on restart)
```

### Chat not showing real-time updates
```bash
# Refresh browser F5 or Cmd+R
# Check browser console for errors (F12 → Console tab)
# Ensure backend is running: curl http://localhost:8001/api/health
```

### Approvals panel not showing
```bash
# Role switcher may need to be added to DashboardView
# Integrate RoleSwitcher, SalesOrderList, AuditLogPanel components
# See INTEGRATION_GUIDE.md for code examples
```

---

## Performance Notes

- **Seeding time:** ~5 seconds (MongoDB) or ~2 seconds (in-memory)
- **Dashboard load:** <500ms
- **Chat response:** <2 seconds (includes ERP API calls)
- **Audit log query:** <1 second for 10+ entries

---

## Advanced: Customize Demo

To modify demo scenario, edit `backend/seed_hackathon_demo.py`:

```python
# Change approval threshold
HIGH_VALUE_THRESHOLD = 100000  # Instead of 50000

# Add more customers
DEMO_CUSTOMERS.append({
    "customer_name": "Your Company",
    ...
})

# Modify sales orders
DEMO_SALES_ORDERS.append({
    "order_id": "SO-2024-00105",
    "customer_name": "Acme",
    "grand_total": 250000,
    ...
})

# Re-seed
curl -X POST http://localhost:8001/api/auth/seed-demo
```

---

## Next Steps: Production Deployment

The demo uses:
- ✅ Real ERPNext API integration (ERP_MOCK_MODE=false for live)
- ✅ MongoDB for persistence (set MONGO_URL env var)
- ✅ Azure OpenAI for AI (configure AZURE_OPENAI_* env vars)
- ✅ RBAC decorators ready for real auth

To go production, update `.env`:
```bash
ERP_URL=https://your-erp.erpnext.com
ERP_API_KEY=your_key
ERP_API_SECRET=your_secret
ERP_MOCK_MODE=false  # Use real ERP

MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/agenterp

AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
```

---

**Happy demoing! 🚀**
