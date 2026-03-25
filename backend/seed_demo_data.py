"""Seed demo data for management scenario - Users, Orders, Approvals, Audit logs."""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import logging

from database import db, mongodb_available
from models.enterprise import UserRole, ApprovalStatus, AuditAction
from services.auth_service import auth_service
from services.approval_service import approval_service
from services.audit_service import audit_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== DEMO DATA ==============

DEMO_USERS = [
    {
        "email": "admin@agenterp.com",
        "password": "admin123",
        "name": "Admin User",
        "role": UserRole.ADMIN,
        "company": None  # Admin sees all
    },
    {
        "email": "manager@agenterp.com",
        "password": "manager123",
        "name": "Manager - Approvals",
        "role": UserRole.MANAGER,
        "company": "TechCorp Solutions"
    },
    {
        "email": "operator@agenterp.com",
        "password": "operator123",
        "name": "Operator - Order Creator",
        "role": UserRole.OPERATOR,
        "company": "TechCorp Solutions"
    },
    {
        "email": "viewer@agenterp.com",
        "password": "viewer123",
        "name": "Viewer - Read Only",
        "role": UserRole.VIEWER,
        "company": "TechCorp Solutions"
    },
]

DEMO_CUSTOMERS = [
    {
        "name": "Acme Corporation",
        "contact_email": "contact@acme.com",
        "phone": "+91-9876543210",
        "city": "Mumbai",
        "country": "India",
        "credit_limit": 500000,
        "outstanding_balance": 0
    },
    {
        "name": "Global Tech Industries",
        "contact_email": "sales@globaltech.com",
        "phone": "+91-9123456789",
        "city": "Bangalore",
        "country": "India",
        "credit_limit": 750000,
        "outstanding_balance": 0
    },
    {
        "name": "Innovation Labs Inc",
        "contact_email": "procurement@innovlabs.com",
        "phone": "+91-8765432109",
        "city": "Hyderabad",
        "country": "India",
        "credit_limit": 250000,
        "outstanding_balance": 0
    },
    {
        "name": "Enterprise Solutions Ltd",
        "contact_email": "orders@enterprise.com",
        "phone": "+91-7654321098",
        "city": "Delhi",
        "country": "India",
        "credit_limit": 1000000,
        "outstanding_balance": 0
    },
]

DEMO_SALES_ORDERS = [
    # High-value order 1 (requires approval)
    {
        "customer": "Acme Corporation",
        "order_date": datetime.now(timezone.utc) - timedelta(days=2),
        "items": [
            {"item_name": "Enterprise License", "qty": 10, "rate": 5000},
            {"item_name": "Support Package", "qty": 5, "rate": 2000},
        ],
        "grand_total": 60000,
        "status": "pending_approval",
        "approval_required": True,
        "requires_approval_reason": "Order value ₹60,000 exceeds threshold of ₹50,000"
    },
    # High-value order 2 (requires approval)
    {
        "customer": "Global Tech Industries",
        "order_date": datetime.now(timezone.utc) - timedelta(days=1),
        "items": [
            {"item_name": "Cloud Infrastructure", "qty": 1, "rate": 75000},
            {"item_name": "Premium Support", "qty": 2, "rate": 10000},
        ],
        "grand_total": 95000,
        "status": "pending_approval",
        "approval_required": True,
        "requires_approval_reason": "Order value ₹95,000 exceeds threshold of ₹50,000"
    },
    # Normal order (no approval needed)
    {
        "customer": "Innovation Labs Inc",
        "order_date": datetime.now(timezone.utc) - timedelta(days=3),
        "items": [
            {"item_name": "Basic License", "qty": 5, "rate": 3000},
        ],
        "grand_total": 15000,
        "status": "completed",
        "approval_required": False,
        "requires_approval_reason": None
    },
    # Normal order (no approval needed)
    {
        "customer": "Enterprise Solutions Ltd",
        "order_date": datetime.now(timezone.utc) - timedelta(days=5),
        "items": [
            {"item_name": "Consulting Hours", "qty": 40, "rate": 500},
        ],
        "grand_total": 20000,
        "status": "completed",
        "approval_required": False,
        "requires_approval_reason": None
    },
    # Approved high-value order
    {
        "customer": "Acme Corporation",
        "order_date": datetime.now(timezone.utc) - timedelta(days=7),
        "items": [
            {"item_name": "Enterprise Suite", "qty": 1, "rate": 55000},
        ],
        "grand_total": 55000,
        "status": "approved",
        "approval_required": True,
        "requires_approval_reason": "Order value ₹55,000 exceeds threshold of ₹50,000",
        "approved_by": "manager@agenterp.com",
        "approval_date": datetime.now(timezone.utc) - timedelta(days=6)
    },
]


async def seed_users() -> Dict[str, str]:
    """Seed demo users and return user IDs."""
    logger.info("🔐 Seeding demo users...")
    user_ids = {}
    
    for user_data in DEMO_USERS:
        try:
            # Check if user exists
            user = await db["users"].find_one({"email": user_data["email"]})
            if user:
                logger.info(f"  ✓ User exists: {user_data['email']}")
                user_ids[user_data["email"]] = user["id"]
                continue
            
            # Create user via auth service
            result = await auth_service.register_user(
                type("UserCreate", (), {
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "name": user_data["name"],
                    "role": user_data["role"],
                    "company": user_data["company"]
                })
            )
            
            if result["status"] == "success":
                user_ids[user_data["email"]] = result["user"]["id"]
                logger.info(f"  ✓ Created: {user_data['email']} ({user_data['role'].value})")
            else:
                logger.error(f"  ✗ Failed to create {user_data['email']}: {result['message']}")
        except Exception as e:
            logger.error(f"  ✗ Error seeding user {user_data['email']}: {e}")
    
    return user_ids


async def seed_customers() -> Dict[str, str]:
    """Seed demo customers and return customer IDs."""
    logger.info("\n👥 Seeding demo customers...")
    customer_ids = {}
    
    for customer_data in DEMO_CUSTOMERS:
        try:
            # Check if exists
            existing = await db["customers"].find_one({"name": customer_data["name"]})
            if existing:
                logger.info(f"  ✓ Customer exists: {customer_data['name']}")
                customer_ids[customer_data["name"]] = existing.get("id") or customer_data["name"]
                continue
            
            customer_id = str(uuid.uuid4())
            customer_doc = {
                "id": customer_id,
                "name": customer_data["name"],
                "contact_email": customer_data["contact_email"],
                "phone": customer_data["phone"],
                "city": customer_data["city"],
                "country": customer_data["country"],
                "credit_limit": customer_data["credit_limit"],
                "outstanding_balance": customer_data["outstanding_balance"],
                "created_at": datetime.now(timezone.utc)
            }
            
            await db["customers"].insert_one(customer_doc)
            customer_ids[customer_data["name"]] = customer_id
            logger.info(f"  ✓ Created: {customer_data['name']}")
        except Exception as e:
            logger.error(f"  ✗ Error seeding customer {customer_data['name']}: {e}")
    
    return customer_ids


async def seed_sales_orders(user_ids: Dict[str, str], customer_ids: Dict[str, str]):
    """Seed demo sales orders and associated approvals."""
    logger.info("\n📋 Seeding demo sales orders...")
    operator_id = None
    manager_id = None
    
    # Get IDs
    for email, uid in user_ids.items():
        if "operator" in email:
            operator_id = uid
        if "manager" in email:
            manager_id = uid
    
    order_count = 0
    for order_data in DEMO_SALES_ORDERS:
        try:
            order_id = str(uuid.uuid4())
            customer_id = customer_ids.get(order_data["customer"], order_data["customer"])
            
            order_doc = {
                "id": order_id,
                "customer": order_data["customer"],
                "customer_id": customer_id,
                "order_date": order_data["order_date"],
                "items": order_data["items"],
                "grand_total": order_data["grand_total"],
                "status": order_data["status"],
                "created_by": "operator@agenterp.com",
                "created_by_id": operator_id,
                "approval_required": order_data["approval_required"],
                "approval_notes": order_data.get("requires_approval_reason"),
            }
            
            if order_data["status"] == "approved":
                order_doc["approved_by"] = order_data.get("approved_by")
                order_doc["approved_by_id"] = manager_id
                order_doc["approval_date"] = order_data.get("approval_date")
            
            await db["sales_orders"].insert_one(order_doc)
            order_count += 1
            
            # Create approval request if needed
            if order_data["approval_required"]:
                approval_id = str(uuid.uuid4())
                approval_doc = {
                    "id": approval_id,
                    "requester_id": operator_id,
                    "requester_email": "operator@agenterp.com",
                    "requester_role": "operator",
                    "order_id": order_id,
                    "action_type": "create_order",
                    "resource_type": "Sales Order",
                    "resource_data": order_doc,
                    "rule_triggered": "high_value_order",
                    "reason": order_data.get("requires_approval_reason"),
                    "status": "approved" if order_data["status"] == "approved" else "pending",
                    "created_at": order_data["order_date"],
                    "requested_at": order_data["order_date"],
                }
                
                if order_data["status"] == "approved":
                    approval_doc["approved_at"] = order_data.get("approval_date")
                    approval_doc["approved_by"] = manager_id
                    approval_doc["approved_by_email"] = "manager@agenterp.com"
                
                await db["approval_requests"].insert_one(approval_doc)
            
            logger.info(f"  ✓ Created: Order {order_id[:8]}... (₹{order_data['grand_total']:,}) - {order_data['status']}")
        except Exception as e:
            logger.error(f"  ✗ Error seeding order: {e}")
    
    logger.info(f"  Total: {order_count} orders created")


async def seed_audit_logs(user_ids: Dict[str, str]):
    """Seed demo audit logs."""
    logger.info("\n📊 Seeding demo audit logs...")
    
    audit_entries = [
        {
            "user_id": user_ids.get("admin@agenterp.com"),
            "user_email": "admin@agenterp.com",
            "user_role": "admin",
            "action": AuditAction.USER_LOGIN.value,
            "resource_type": "User",
            "result": "success",
            "timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
        },
        {
            "user_id": user_ids.get("operator@agenterp.com"),
            "user_email": "operator@agenterp.com",
            "user_role": "operator",
            "action": AuditAction.CREATE_ORDER.value,
            "resource_type": "Sales Order",
            "resource_id": "order_1",
            "result": "pending",
            "result_message": "Order created, pending approval due to high value",
            "approval_required": True,
            "timestamp": datetime.now(timezone.utc) - timedelta(hours=1)
        },
        {
            "user_id": user_ids.get("manager@agenterp.com"),
            "user_email": "manager@agenterp.com",
            "user_role": "manager",
            "action": AuditAction.APPROVE_REQUEST.value,
            "resource_type": "Sales Order",
            "resource_id": "order_1",
            "result": "success",
            "result_message": "Order approved and processed",
            "timestamp": datetime.now(timezone.utc) - timedelta(minutes=30)
        },
        {
            "user_id": user_ids.get("viewer@agenterp.com"),
            "user_email": "viewer@agenterp.com",
            "user_role": "viewer",
            "action": AuditAction.QUERY_DATA.value,
            "resource_type": "Sales Order",
            "result": "success",
            "timestamp": datetime.now(timezone.utc) - timedelta(minutes=15)
        },
    ]
    
    log_count = 0
    for entry in audit_entries:
        try:
            if entry["user_id"]:  # Only create if user exists
                log_id = str(uuid.uuid4())
                entry["id"] = log_id
                await db["audit_logs"].insert_one(entry)
                log_count += 1
        except Exception as e:
            logger.error(f"  ✗ Error seeding audit log: {e}")
    
    logger.info(f"  ✓ Created: {log_count} audit log entries")


async def main():
    """Run all seeding functions."""
    if not mongodb_available:
        logger.warning("⚠️  MongoDB not available, skipping seed (using in-memory)")
        return
    
    logger.info("=" * 60)
    logger.info("🌱 SEEDING DEMO DATA FOR AGENTERP").center(60)
    logger.info("=" * 60)
    
    try:
        user_ids = await seed_users()
        customer_ids = await seed_customers()
        await seed_sales_orders(user_ids, customer_ids)
        await seed_audit_logs(user_ids)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ SEEDING COMPLETE!".center(60))
        logger.info("=" * 60)
        logger.info("\n🔐 Demo Users:")
        for user in DEMO_USERS:
            logger.info(f"  • {user['email']} / {user['password']} ({user['role'].value})")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"\n❌ Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
