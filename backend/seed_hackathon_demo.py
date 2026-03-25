"""
Robust demo seed scenario for Microsoft AI Hackathon.

Hero Scenario: "High-Value Order Recovery & Approval Automation"

This script seeds:
1. ERPNext data (customers, items, sales orders)
2. Local MongoDB data (chat history, audit logs, dashboard metrics)
3. Deterministic, repeatable demo data
4. Complete workflow from order creation → manager approval → visibility

The demo tells a coherent story:
- Operator creates high-value orders
- System flags orders >50000 for approval
- Manager reviews and approves
- Audit trail shows complete lifecycle
- Chat history demonstrates natural interaction
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import logging

from database import db, mongodb_available
from models.enterprise import UserRole, ApprovalStatus, AuditAction
from models import ChatSession, ChatMessage
from services.auth_service import auth_service
from services.approval_service import approval_service
from services.audit_service import audit_service
from services.erp_service import erp_service
from services.erp_entity_service import erp_entity_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# DETERMINISTIC DEMO DATA (Fixed, Repeatable)
# ============================================================

DEMO_USERS = [
    {
        "email": "admin@agenterp.com",
        "password": "admin123",
        "name": "Admin User",
        "role": UserRole.ADMIN,
        "company": None
    },
    {
        "email": "manager@agenterp.com",
        "password": "manager123",
        "name": "Sarah Johnson",
        "role": UserRole.MANAGER,
        "company": "TechCorp Solutions"
    },
    {
        "email": "operator@agenterp.com",
        "password": "operator123",
        "name": "Raj Patel",
        "role": UserRole.OPERATOR,
        "company": "TechCorp Solutions"
    },
    {
        "email": "viewer@agenterp.com",
        "password": "viewer123",
        "name": "Lisa Chen",
        "role": UserRole.VIEWER,
        "company": "TechCorp Solutions"
    },
]

# ERPNext Customers (will be created via ERP API)
DEMO_CUSTOMERS = [
    {
        "customer_name": "Acme Manufacturing",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-9876543210",
        "email": "contact@acme.com",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "credit_limit": 1000000
    },
    {
        "customer_name": "Global Tech Industries",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-9123456789",
        "email": "procurement@globaltech.com",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "credit_limit": 1500000
    },
    {
        "customer_name": "Innovation Labs Inc",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-8765432109",
        "email": "orders@innovlabs.com",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "credit_limit": 750000
    },
    {
        "customer_name": "Enterprise Solutions Ltd",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-7654321098",
        "email": "buyadmin@enterprise.com",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "credit_limit": 2000000
    },
    {
        "customer_name": "Cloud Systems Partners",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-6543210987",
        "email": "orders@cloudsys.com",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "credit_limit": 1200000
    },
    {
        "customer_name": "Data Analytics Corp",
        "customer_type": "Company",
        "territory": "India",
        "mobile_no": "+91-5432109876",
        "email": "procurement@dataanalytics.com",
        "city": "Gurgaon",
        "state": "Haryana",
        "country": "India",
        "credit_limit": 800000
    },
]

# ERPNext Items (inventory items)
DEMO_ITEMS = [
    {
        "item_code": "SERVER-001",
        "item_name": "Enterprise Server - 64GB RAM",
        "description": "High-performance server with 64GB RAM and dual CPU",
        "item_group": "Hardware",
        "uom": "Nos",
        "standard_rate": 150000
    },
    {
        "item_code": "LICENSE-001",
        "item_name": "Enterprise Software License",
        "description": "Annual enterprise software license",
        "item_group": "Software",
        "uom": "Nos",
        "standard_rate": 50000
    },
    {
        "item_code": "CLOUD-001",
        "item_name": "Cloud Storage - 1TB/Year",
        "description": "1TB cloud storage subscription for one year",
        "item_group": "Services",
        "uom": "Nos",
        "standard_rate": 12000
    },
    {
        "item_code": "SUPPORT-001",
        "item_name": "Premium Support Package",
        "description": "24/7 premium technical support for 1 year",
        "item_group": "Services",
        "uom": "Nos",
        "standard_rate": 25000
    },
    {
        "item_code": "NETWORK-001",
        "item_name": "Network Switch - 48 Port",
        "description": "Enterprise-grade 48-port network switch",
        "item_group": "Hardware",
        "uom": "Nos",
        "standard_rate": 85000
    },
    {
        "item_code": "TRAINING-001",
        "item_name": "Training Services",
        "description": "On-site training and implementation services",
        "item_group": "Services",
        "uom": "Days",
        "standard_rate": 10000
    },
]

# Base timestamp for all demo data (for consistency and storytelling)
DEMO_BASE_TIME = datetime.now(timezone.utc) - timedelta(days=7)

# Sales orders - the HERO SCENARIO
# This tells the story of "High-Value Order Recovery & Approval Automation"
DEMO_SALES_ORDERS = [
    # ORDER 1: High-value pending approval (created 5 days ago)
    {
        "order_id": "SO-2024-00101",
        "customer_name": "Global Tech Industries",
        "transaction_date": (DEMO_BASE_TIME + timedelta(days=2)).isoformat(),
        "items": [
            {"item_code": "SERVER-001", "qty": 2, "rate": 150000, "item_name": "Enterprise Server - 64GB RAM"},
            {"item_code": "NETWORK-001", "qty": 1, "rate": 85000, "item_name": "Network Switch - 48 Port"},
            {"item_code": "SUPPORT-001", "qty": 3, "rate": 25000, "item_name": "Premium Support Package"},
        ],
        "grand_total": 545000,
        "status": "pending_approval",
        "priority": "high",
        "description": "Infrastructure upgrade project - Q1 2024"
    },
    # ORDER 2: High-value pending approval (created 4 days ago - later approved)
    {
        "order_id": "SO-2024-00102",
        "customer_name": "Enterprise Solutions Ltd",
        "transaction_date": (DEMO_BASE_TIME + timedelta(days=3)).isoformat(),
        "items": [
            {"item_code": "LICENSE-001", "qty": 20, "rate": 50000, "item_name": "Enterprise Software License"},
            {"item_code": "TRAINING-001", "qty": 5, "rate": 10000, "item_name": "Training Services"},
        ],
        "grand_total": 1050000,
        "status": "approved",
        "priority": "high",
        "description": "Enterprise software deployment - 20 licenses"
    },
    # ORDER 3: Normal order below threshold (created 6 days ago)
    {
        "order_id": "SO-2024-00103",
        "customer_name": "Acme Manufacturing",
        "transaction_date": (DEMO_BASE_TIME + timedelta(days=1)).isoformat(),
        "items": [
            {"item_code": "CLOUD-001", "qty": 3, "rate": 12000, "item_name": "Cloud Storage - 1TB/Year"},
            {"item_code": "SUPPORT-001", "qty": 1, "rate": 25000, "item_name": "Premium Support Package"},
        ],
        "grand_total": 61000,
        "status": "submitted",
        "priority": "normal",
        "description": "Monthly recurring subscription"
    },
    # ORDER 4: Delayed order (created long ago, still in progress)
    {
        "order_id": "SO-2024-00099",
        "customer_name": "Innovation Labs Inc",
        "transaction_date": (DEMO_BASE_TIME - timedelta(days=10)).isoformat(),
        "items": [
            {"item_code": "SERVER-001", "qty": 1, "rate": 150000, "item_name": "Enterprise Server - 64GB RAM"},
            {"item_code": "CLOUD-001", "qty": 5, "rate": 12000, "item_name": "Cloud Storage - 1TB/Year"},
        ],
        "grand_total": 210000,
        "status": "to_deliver",
        "priority": "normal",
        "description": "Delayed infrastructure delivery - waiting for approval"
    },
    # ORDER 5: Completed order (shows workflow success)
    {
        "order_id": "SO-2024-00095",
        "customer_name": "Cloud Systems Partners",
        "transaction_date": (DEMO_BASE_TIME - timedelta(days=12)).isoformat(),
        "items": [
            {"item_code": "SUPPORT-001", "qty": 2, "rate": 25000, "item_name": "Premium Support Package"},
        ],
        "grand_total": 50000,
        "status": "delivered",
        "priority": "normal",
        "description": "Support renewal - completed successfully"
    },
    # ORDER 6: Another high-value pending (shows pattern of high-value orders)
    {
        "order_id": "SO-2024-00104",
        "customer_name": "Data Analytics Corp",
        "transaction_date": (DEMO_BASE_TIME + timedelta(days=4)).isoformat(),
        "items": [
            {"item_code": "LICENSE-001", "qty": 10, "rate": 50000, "item_name": "Enterprise Software License"},
            {"item_code": "CLOUD-001", "qty": 10, "rate": 12000, "item_name": "Cloud Storage - 1TB/Year"},
        ],
        "grand_total": 620000,
        "status": "pending_approval",
        "priority": "high",
        "description": "Data analytics platform deployment"
    },
]

# ============================================================
# SEEDING FUNCTIONS
# ============================================================

async def seed_users() -> Dict[str, str]:
    """
    Seed demo users and return mapping of email -> user_id.
    """
    logger.info("🔐 Seeding demo users...")
    user_ids = {}
    
    try:
        for user_data in DEMO_USERS:
            try:
                # Try to create user via auth service
                user_doc = {
                    "id": str(uuid.uuid4()),
                    "email": user_data["email"],
                    "password_hash": "dummy_hash",  # Won't be verified in demo
                    "name": user_data["name"],
                    "role": user_data["role"],
                    "company": user_data["company"],
                    "created_at": DEMO_BASE_TIME.isoformat(),
                    "last_login": None
                }
                
                # Check if user exists
                existing = await db.users.find_one({"email": user_data["email"]})
                if not existing:
                    await db.users.insert_one(user_doc)
                    logger.info(f"  ✓ Created user: {user_data['email']} ({user_data['role']})")
                else:
                    user_doc["id"] = existing.get("id", existing.get("_id"))
                    logger.info(f"  ✓ User already exists: {user_data['email']}")
                
                user_ids[user_data["email"]] = user_doc["id"]
            except Exception as e:
                logger.error(f"  ✗ Error creating user {user_data['email']}: {e}")
        
        logger.info(f"✅ Seeded {len(user_ids)} users\n")
        return user_ids
    except Exception as e:
        logger.error(f"❌ Error in seed_users: {e}")
        raise


async def seed_erp_customers() -> Dict[str, str]:
    """
    Seed customers into ERPNext via API and return customer_name -> id mapping.
    """
    logger.info("👥 Seeding ERPNext customers...")
    customer_ids = {}
    
    try:
        for customer_data in DEMO_CUSTOMERS:
            try:
                # Check if customer already exists
                exists = await erp_service.check_customer(customer_data["customer_name"])
                
                if not exists.get("exists"):
                    # Create customer
                    create_result = await erp_service.create_customer(
                        customer=type('Customer', (), {
                            'customer_name': customer_data['customer_name'],
                            'customer_type': customer_data['customer_type'],
                            'territory': customer_data['territory']
                        })()
                    )
                    
                    if create_result.get("status") == "success":
                        logger.info(f"  ✓ Created customer: {customer_data['customer_name']}")
                    else:
                        logger.warning(f"  ⚠ Customer creation returned: {create_result.get('message')}")
                else:
                    logger.info(f"  ✓ Customer already exists: {customer_data['customer_name']}")
                
                customer_ids[customer_data["customer_name"]] = customer_data["customer_name"]
            except Exception as e:
                logger.error(f"  ✗ Error creating customer {customer_data['customer_name']}: {e}")
        
        logger.info(f"✅ Seeded {len(customer_ids)} customers\n")
        return customer_ids
    except Exception as e:
        logger.error(f"❌ Error in seed_erp_customers: {e}")
        raise


async def seed_erp_items() -> Dict[str, str]:
    """
    Seed items into ERPNext via generic entity service.
    """
    logger.info("📦 Seeding ERPNext items...")
    item_ids = {}
    
    try:
        for item_data in DEMO_ITEMS:
            try:
                # Check if item exists
                existing = await erp_entity_service.entity_exists("Item", item_data["item_code"])
                
                if not existing:
                    # Create item via generic service
                    result = await erp_entity_service.create(
                        doctype="Item",
                        data={
                            "item_code": item_data["item_code"],
                            "item_name": item_data["item_name"],
                            "description": item_data["description"],
                            "item_group": item_data["item_group"],
                            "stock_uom": item_data["uom"],
                            "is_stock_item": 1 if "HARDWARE" in item_data["item_group"].upper() 
                                            else 0
                        },
                        skip_validation=True
                    )
                    
                    if result.get("status") == "success":
                        logger.info(f"  ✓ Created item: {item_data['item_code']}")
                    else:
                        logger.warning(f"  ⚠ Item creation: {result.get('message')}")
                else:
                    logger.info(f"  ✓ Item already exists: {item_data['item_code']}")
                
                item_ids[item_data["item_code"]] = item_data["item_code"]
            except Exception as e:
                logger.warning(f"  ⚠ Error creating item {item_data['item_code']}: {e}")
        
        logger.info(f"✅ Seeded {len(item_ids)} items\n")
        return item_ids
    except Exception as e:
        logger.error(f"⚠ Note: Item creation may fail in mock mode (expected): {e}")
        raise


async def seed_erp_sales_orders(customer_ids: Dict[str, str]) -> Dict[str, str]:
    """
    Seed sales orders into ERPNext and local MongoDB with approval workflow.
    """
    logger.info("📋 Seeding ERPNext sales orders...")
    order_ids = {}
    local_orders = []
    
    try:
        for order_data in DEMO_SALES_ORDERS:
            try:
                # Create in ERPNext
                create_result = await erp_service.create_sales_order(
                    sales_order=type('SalesOrder', (), {
                        'customer': order_data['customer_name'],
                        'transaction_date': order_data['transaction_date'],
                        'items': [
                            type('SalesOrderItem', (), {
                                'item_code': item['item_code'],
                                'qty': item['qty']
                            })()
                            for item in order_data['items']
                        ]
                    })()
                )
                
                if create_result.get("status") == "success":
                    logger.info(f"  ✓ Created order: {order_data['order_id']} (₹{order_data['grand_total']:,})")
                else:
                    logger.warning(f"  ⚠ Order creation: {create_result.get('message')}")
                
                # Store local copy for MongoDB
                local_order = {
                    "id": order_data["order_id"],
                    "doctype": "Sales Order",
                    "order_id": order_data["order_id"],
                    "customer": order_data["customer_name"],
                    "transaction_date": order_data["transaction_date"],
                    "items": order_data["items"],
                    "grand_total": order_data["grand_total"],
                    "status": order_data["status"],
                    "priority": order_data["priority"],
                    "description": order_data["description"],
                    "created_at": order_data["transaction_date"],
                    "operator": "operator@agenterp.com"
                }
                
                # Add approval request if high-value
                if order_data["grand_total"] > 50000 and order_data["status"] == "pending_approval":
                    local_order["approval_required"] = True
                    local_order["approval_status"] = "pending"
                    local_order["approval_id"] = str(uuid.uuid4())
                elif order_data["status"] == "approved":
                    local_order["approval_required"] = True
                    local_order["approval_status"] = "approved"
                    local_order["approval_id"] = str(uuid.uuid4())
                    local_order["approved_by"] = "manager@agenterp.com"
                    local_order["approved_at"] = (DEMO_BASE_TIME + timedelta(days=1)).isoformat()
                
                local_orders.append(local_order)
                order_ids[order_data["order_id"]] = order_data["order_id"]
            except Exception as e:
                logger.error(f"  ✗ Error creating order {order_data['order_id']}: {e}")
        
        # Store all orders in MongoDB
        if local_orders:
            # Clear existing orders first
            await db.sales_orders.delete_many({})
            await db.sales_orders.insert_many(local_orders)
            logger.info(f"✅ Seeded {len(local_orders)} sales orders in MongoDB")
        
        logger.info(f"✅ Total sales value: ₹{sum(o['grand_total'] for o in local_orders):,}\n")
        return order_ids
    except Exception as e:
        logger.error(f"❌ Error in seed_erp_sales_orders: {e}")
        raise


async def seed_approval_requests(order_ids: Dict[str, str], user_ids: Dict[str, str]):
    """
    Seed approval requests based on high-value orders.
    """
    logger.info("✅ Seeding approval requests...")
    approval_count = 0
    
    try:
        # Find all high-value orders in MongoDB
        high_value_orders = await db.sales_orders.find({
            "grand_total": {"$gt": 50000},
            "approval_status": {"$in": ["pending", "approved"]}
        })
        
        for order in high_value_orders:
            # Create approval request
            approval_request = {
                "id": str(uuid.uuid4()),
                "order_id": order["order_id"],
                "doctype": "Approval Request",
                "customer": order["customer"],
                "order_value": order["grand_total"],
                "requester_email": "operator@agenterp.com",
                "requester_id": user_ids.get("operator@agenterp.com", ""),
                "status": order.get("approval_status", "pending"),
                "reason": f"Order value ₹{order['grand_total']:,} exceeds ₹50,000 threshold",
                "created_at": order["transaction_date"],
                "notes": order.get("description", "")
            }
            
            # Add approval details if approved
            if order.get("approval_status") == "approved":
                approval_request["approved_by"] = "manager@agenterp.com"
                approval_request["approved_by_id"] = user_ids.get("manager@agenterp.com", "")
                approval_request["approved_at"] = (DEMO_BASE_TIME + timedelta(days=1)).isoformat()
                approval_request["approval_notes"] = "Approved based on positive credit history"
            
            # Check if request already exists
            existing = await db.approval_requests.find_one({"order_id": order["order_id"]})
            if not existing:
                await db.approval_requests.insert_one(approval_request)
                approval_count += 1
                logger.info(f"  ✓ Created approval request for {order['order_id']}")
        
        logger.info(f"✅ Seeded {approval_count} approval requests\n")
    except Exception as e:
        logger.error(f"❌ Error in seed_approval_requests: {e}")


async def seed_chat_history(user_ids: Dict[str, str], order_ids: Dict[str, str]):
    """
    Seed realistic chat history that demonstrates the hero scenario.
    Chat shows: operator creating orders → system flagging → manager approving.
    """
    logger.info("💬 Seeding realistic chat history...")
    
    try:
        # Chat sessions for different users
        chat_sessions = []
        chat_messages = []
        
        # Session 1: Operator creating orders
        session_1 = {
            "id": "session-001",
            "created_at": (DEMO_BASE_TIME + timedelta(days=2)).isoformat(),
            "updated_at": (DEMO_BASE_TIME + timedelta(days=2, hours=3)).isoformat(),
            "user_id": user_ids.get("operator@agenterp.com", ""),
            "user_email": "operator@agenterp.com",
            "title": "Creating Q1 Sales Orders",
            "company": "TechCorp Solutions"
        }
        chat_sessions.append(session_1)
        
        # Messages in session 1
        session_1_messages = [
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-001",
                "role": "user",
                "content": "Create a sales order for Global Tech Industries with 2 enterprise servers, 1 network switch, and 3 support packages",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=0)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-001",
                "role": "assistant",
                "content": "📋 I've created sales order SO-2024-00101 for Global Tech Industries.\n\n**Order Details:**\n- 2x Enterprise Server - 64GB RAM @ ₹150,000 = ₹300,000\n- 1x Network Switch - 48 Port @ ₹85,000 = ₹85,000\n- 3x Premium Support Package @ ₹25,000 = ₹75,000\n\n**Total: ₹545,000**\n\n⚠️ **Important:** This order exceeds the ₹50,000 approval threshold and requires manager approval. I've flagged it for manager@agenterp.com.",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=1)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-001",
                "role": "user",
                "content": "Good. Now create another order for Enterprise Solutions Ltd - 20 licenses and 5 training days",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=5)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-001",
                "role": "assistant",
                "content": "✅ I've created sales order SO-2024-00102 for Enterprise Solutions Ltd.\n\n**Order Details:**\n- 20x Enterprise Software License @ ₹50,000 = ₹1,000,000\n- 5x Training Services @ ₹10,000 = ₹50,000\n\n**Total: ₹1,050,000**\n\n🔴 **CRITICAL:** This is a very high-value order (₹1,050,000). It requires immediate manager approval. System has auto-flagged for management review.",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=6)).isoformat(),
                "type": "text"
            },
        ]
        chat_messages.extend(session_1_messages)
        
        # Session 2: Manager reviewing approvals
        session_2 = {
            "id": "session-002",
            "created_at": (DEMO_BASE_TIME + timedelta(days=3)).isoformat(),
            "updated_at": (DEMO_BASE_TIME + timedelta(days=3, hours=2)).isoformat(),
            "user_id": user_ids.get("manager@agenterp.com", ""),
            "user_email": "manager@agenterp.com",
            "title": "Pending Approvals Review",
            "company": "TechCorp Solutions"
        }
        chat_sessions.append(session_2)
        
        # Messages in session 2
        session_2_messages = [
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "user",
                "content": "Show me all pending approvals above ₹50,000",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=0)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "assistant",
                "content": "📊 **Pending Approvals Summary**\n\nYou have 2 high-value orders awaiting approval:\n\n1. **SO-2024-00101** - Global Tech Industries\n   - Amount: ₹545,000\n   - Items: 2x Servers, 1x Switch, 3x Support\n   - Created: 2024-01-02\n   - Status: Pending Approval\n\n2. **SO-2024-00104** - Data Analytics Corp\n   - Amount: ₹620,000\n   - Items: 10x Licenses, 10x Cloud Storage\n   - Created: 2024-01-04\n   - Status: Pending Approval\n\n3. **SO-2024-00102** - Enterprise Solutions Ltd\n   - Amount: ₹1,050,000 ⚠️ VERY HIGH VALUE\n   - Items: 20x Licenses, 5x Training\n   - Created: 2024-01-03\n   - Status: Pending Approval\n\nTotal pending: ₹2,215,000",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=1)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "user",
                "content": "Check credit history for Global Tech Industries - are they reliable?",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=5)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "assistant",
                "content": "✅ **Credit Assessment for Global Tech Industries**\n\n- **Credit Limit:** ₹1,500,000\n- **Current Outstanding:** ₹0\n- **Payment History:** Excellent (on-time payments for 8+ orders)\n- **Account Age:** 18 months\n- **Risk Level:** LOW ✓\n\n**Recommendation:** Safe to approve. Customer has demonstrated reliability and adequate credit capacity.",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=6)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "user",
                "content": "Approve SO-2024-00101 and SO-2024-00102",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=10)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-002",
                "role": "assistant",
                "content": "✅ **Approvals Processed**\n\n✓ **SO-2024-00101** (Global Tech Industries - ₹545,000)\n  - Status changed from Pending to Approved\n  - Approved by: Sarah Johnson (manager@agenterp.com)\n  - Timestamp: 2024-01-03 10:45 AM\n\n✓ **SO-2024-00102** (Enterprise Solutions Ltd - ₹1,050,000)\n  - Status changed from Pending to Approved\n  - Approved by: Sarah Johnson (manager@agenterp.com)\n  - Timestamp: 2024-01-03 10:46 AM\n  - Note: High-value order approved based on positive credit profile\n\n**Total Approved Today:** ₹1,595,000\n\n📧 Notifications sent to operator and sales teams.",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=11)).isoformat(),
                "type": "text"
            },
        ]
        chat_messages.extend(session_2_messages)
        
        # Session 3: Admin dashboard query
        session_3 = {
            "id": "session-003",
            "created_at": (DEMO_BASE_TIME + timedelta(days=4)).isoformat(),
            "updated_at": (DEMO_BASE_TIME + timedelta(days=4, hours=1)).isoformat(),
            "user_id": user_ids.get("admin@agenterp.com", ""),
            "user_email": "admin@agenterp.com",
            "title": "Executive Dashboard Review",
            "company": None
        }
        chat_sessions.append(session_3)
        
        # Messages in session 3
        session_3_messages = [
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-003",
                "role": "user",
                "content": "How many high-value orders are we processing?",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=4, minutes=0)).isoformat(),
                "type": "text"
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": "session-003",
                "role": "assistant",
                "content": "📊 **High-Value Order Dashboard**\n\n**This Week Summary:**\n- Total Orders: 6\n- High-Value Orders (>₹50K): 4\n- Already Approved: 2 (₹1,595,000)\n- Still Pending: 1 (₹620,000)\n- Total Pipeline: ₹2,215,000\n\n**Status Breakdown:**\n- ✅ Approved: 2 orders\n- ⏳ Pending: 1 order\n- 📦 In Delivery: 1 order\n- ✓ Completed: 1 order\n- 📋 Draft: 1 order\n\n**Performance Metrics:**\n- Average approval time: < 24 hours\n- Approval success rate: 100%\n- Revenue from high-value: ₹2,215,000\n- Risk level: All approved orders: LOW",
                "timestamp": (DEMO_BASE_TIME + timedelta(days=4, minutes=2)).isoformat(),
                "type": "text"
            },
        ]
        chat_messages.extend(session_3_messages)
        
        # Insert sessions
        if chat_sessions:
            await db.chat_sessions.delete_many({})
            await db.chat_sessions.insert_many(chat_sessions)
            logger.info(f"  ✓ Created {len(chat_sessions)} chat sessions")
        
        # Insert messages
        if chat_messages:
            await db.chat_messages.delete_many({})
            await db.chat_messages.insert_many(chat_messages)
            logger.info(f"  ✓ Created {len(chat_messages)} chat messages")
        
        logger.info(f"✅ Seeded realistic chat history\n")
    except Exception as e:
        logger.error(f"❌ Error in seed_chat_history: {e}")
        raise


async def seed_audit_logs(user_ids: Dict[str, str], order_ids: Dict[str, str]):
    """
    Seed comprehensive audit logs showing complete workflow.
    """
    logger.info("📊 Seeding audit logs...")
    
    try:
        audit_logs = []
        
        # Operator creates first order
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("operator@agenterp.com", ""),
            "user_email": "operator@agenterp.com",
            "user_role": "operator",
            "action": "create_order",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00101",
            "input_params": {"customer": "Global Tech Industries", "amount": 545000},
            "result": "success",
            "result_message": "Sales order created successfully",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=1)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # System flags for approval
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": "system",
            "user_email": "system@agenterp.com",
            "user_role": "admin",
            "action": "request_approval",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00101",
            "result": "success",
            "result_message": "High-value order (₹545,000) flagged for manager approval",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=2, minutes=2)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # Operator creates second order
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("operator@agenterp.com", ""),
            "user_email": "operator@agenterp.com",
            "user_role": "operator",
            "action": "create_order",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00102",
            "input_params": {"customer": "Enterprise Solutions Ltd", "amount": 1050000},
            "result": "success",
            "result_message": "Sales order created successfully",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=6)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # System flags for approval (high priority)
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": "system",
            "user_email": "system@agenterp.com",
            "user_role": "admin",
            "action": "request_approval",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00102",
            "result": "success",
            "result_message": "CRITICAL: Very high-value order (₹1,050,000) flagged for immediate manager approval",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=7)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # Manager views approvals
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("manager@agenterp.com", ""),
            "user_email": "manager@agenterp.com",
            "user_role": "manager",
            "action": "query_data",
            "resource_type": "Approval Request",
            "resource_id": None,
            "result": "success",
            "result_message": "Manager queried pending approvals",
            "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=30)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # Manager approves first order
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("manager@agenterp.com", ""),
            "user_email": "manager@agenterp.com",
            "user_role": "manager",
            "action": "approve_request",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00101",
            "result": "success",
            "result_message": "Order approved based on excellent credit history",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=45)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # Manager approves second order
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("manager@agenterp.com", ""),
            "user_email": "manager@agenterp.com",
            "user_role": "manager",
            "action": "approve_request",
            "resource_type": "Sales Order",
            "resource_id": "SO-2024-00102",
            "result": "success",
            "result_message": "High-value order approved - strong customer relationship",
            "approval_required": True,
            "timestamp": (DEMO_BASE_TIME + timedelta(days=3, minutes=46)).isoformat(),
            "company": "TechCorp Solutions"
        })
        
        # Admin reviews logs
        audit_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_ids.get("admin@agenterp.com", ""),
            "user_email": "admin@agenterp.com",
            "user_role": "admin",
            "action": "query_data",
            "resource_type": "Audit Log",
            "resource_id": None,
            "result": "success",
            "result_message": "Admin accessed audit logs for compliance review",
            "timestamp": (DEMO_BASE_TIME + timedelta(days=4, minutes=0)).isoformat()
        })
        
        # Insert audit logs
        if audit_logs:
            await db.audit_logs.delete_many({})
            await db.audit_logs.insert_many(audit_logs)
            logger.info(f"✅ Seeded {len(audit_logs)} audit log entries\n")
    except Exception as e:
        logger.error(f"❌ Error in seed_audit_logs: {e}")
        raise


async def seed_dashboard_metrics(order_ids: Dict[str, str]):
    """
    Seed dashboard metrics/cache for real-time display.
    """
    logger.info("📈 Seeding dashboard metrics...")
    
    try:
        # Calculate metrics from actual orders
        total_orders = len(DEMO_SALES_ORDERS)
        high_value_orders = [o for o in DEMO_SALES_ORDERS if o["grand_total"] > 50000]
        pending_approvals = [o for o in DEMO_SALES_ORDERS if o["status"] == "pending_approval"]
        delayed_orders = [o for o in DEMO_SALES_ORDERS if o["status"] == "to_deliver" 
                         or (o["transaction_date"] < (DEMO_BASE_TIME - timedelta(days=5)).isoformat())]
        completed_orders = [o for o in DEMO_SALES_ORDERS if o["status"] == "delivered"]
        
        total_value = sum(o["grand_total"] for o in DEMO_SALES_ORDERS)
        pending_value = sum(o["grand_total"] for o in pending_approvals)
        
        metrics = {
            "id": "dashboard-metrics",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "orders": {
                "total": total_orders,
                "high_value_count": len(high_value_orders),
                "pending_approvals": len(pending_approvals),
                "delayed_orders": len(delayed_orders),
                "completed_orders": len(completed_orders)
            },
            "values": {
                "total_sales": total_value,
                "pending_approval_value": pending_value,
                "average_order_value": total_value / total_orders if total_orders > 0 else 0,
                "high_value_average": sum(o["grand_total"] for o in high_value_orders) / len(high_value_orders) 
                                     if high_value_orders else 0
            },
            "customers": {
                "total": len(DEMO_CUSTOMERS)
            },
            "approvals": {
                "pending": len([o for o in pending_approvals if o["status"] == "pending_approval"]),
                "approved_this_week": len([o for o in DEMO_SALES_ORDERS if o["status"] == "approved"]),
                "approval_rate": 100
            },
            "summary": f"Platform processing {total_orders} orders totaling ₹{total_value:,}. "
                      f"{len(pending_approvals)} high-value orders pending approval (₹{pending_value:,})."
        }
        
        # Store in MongoDB
        await db.dashboard_metrics.delete_many({})
        await db.dashboard_metrics.insert_one(metrics)
        
        logger.info(f"✅ Seeded dashboard metrics")
        logger.info(f"   - Total Orders: {total_orders}")
        logger.info(f"   - High-Value Orders: {len(high_value_orders)}")
        logger.info(f"   - Pending Approvals: {len(pending_approvals)}")
        logger.info(f"   - Total Value: ₹{total_value:,}")
        logger.info(f"   - Customers: {len(DEMO_CUSTOMERS)}\n")
    except Exception as e:
        logger.error(f"❌ Error in seed_dashboard_metrics: {e}")


async def reset_demo_data():
    """Clear all seeded demo data from MongoDB."""
    logger.info("🔄 Resetting demo data...\n")
    
    try:
        collections = [
            "chat_sessions",
            "chat_messages",
            "sales_orders",
            "approval_requests",
            "audit_logs",
            "dashboard_metrics",
            "users"
        ]
        
        for collection in collections:
            try:
                col = getattr(db, collection)
                result = await col.delete_many({})
                logger.info(f"  ✓ Cleared {collection}")
            except Exception as e:
                logger.warning(f"  ⚠ Could not clear {collection}: {e}")
        
        logger.info("\n✅ Reset complete - ready for fresh seeding\n")
    except Exception as e:
        logger.error(f"❌ Error in reset_demo_data: {e}")


# ============================================================
# MAIN SEED ORCHESTRATION
# ============================================================

async def seed_all(reset: bool = True):
    """
    Main seeding function - orchestrates all seeding operations.
    
    Args:
        reset: If True, clears all demo data before seeding
    """
    logger.info("🚀 Starting Microsoft AI Hackathon Demo Seeding...\n")
    logger.info("=" * 70)
    logger.info("HERO SCENARIO: High-Value Order Recovery & Approval Automation")
    logger.info("=" * 70 + "\n")
    
    try:
        # Step 1: Reset if requested
        if reset:
            await reset_demo_data()
        
        # Step 2: Seed users
        user_ids = await seed_users()
        
        # Step 3: Seed ERPNext data
        customer_ids = await seed_erp_customers()
        await seed_erp_items()  # May fail in mock mode, that's OK
        
        # Step 4: Seed sales orders
        order_ids = await seed_erp_sales_orders(customer_ids)
        
        # Step 5: Seed related local data
        await seed_approval_requests(order_ids, user_ids)
        await seed_chat_history(user_ids, order_ids)
        await seed_audit_logs(user_ids, order_ids)
        await seed_dashboard_metrics(order_ids)
        
        logger.info("=" * 70)
        logger.info("✅ SEEDING COMPLETE!")
        logger.info("=" * 70)
        logger.info("\n🎯 Demo is ready to showcase:")
        logger.info("   1. High-value order detection and flagging")
        logger.info("   2. Manager approval workflow")
        logger.info("   3. Complete audit trail")
        logger.info("   4. Real-time chat integration")
        logger.info("   5. Dashboard analytics\n")
        logger.info("📖 Default demo users:")
        for user in DEMO_USERS:
            logger.info(f"   - {user['email']} / {user['password']} ({user['role']})")
        logger.info()
        
        return {"status": "success", "message": "Demo seeding complete"}
    except Exception as e:
        logger.error(f"\n❌ SEEDING FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# ============================================================
# CLI EXECUTION
# ============================================================

if __name__ == "__main__":
    # Run seeding
    result = asyncio.run(seed_all(reset=True))
    print(f"\n{result}")
