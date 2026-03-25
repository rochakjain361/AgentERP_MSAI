"""Authentication routes - User registration, login, and management."""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import logging
import asyncio

from models.enterprise import UserCreate, UserLogin, UserRole
from services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from token."""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
        
        user = await auth_service.verify_token(token)
        return user
    except Exception:
        return None


async def require_auth(authorization: Optional[str] = Header(None)):
    """Dependency that requires authentication."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


async def require_manager(authorization: Optional[str] = Header(None)):
    """Dependency that requires manager or admin role."""
    user = await require_auth(authorization)
    if user["role"] not in [UserRole.MANAGER.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Manager or admin role required")
    return user


async def require_admin(authorization: Optional[str] = Header(None)):
    """Dependency that requires admin role."""
    user = await require_auth(authorization)
    if user["role"] != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@router.post("/register")
async def register(user_data: UserCreate):
    """Register a new user."""
    result = await auth_service.register_user(user_data)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/login")
async def login(credentials: UserLogin):
    """Login and get access token."""
    result = await auth_service.login_user(credentials.email, credentials.password)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@router.get("/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """Get current user information."""
    return {"status": "success", "user": user}


@router.get("/users")
async def list_users(user: dict = Depends(require_admin)):
    """List all users (admin only)."""
    return await auth_service.list_users()


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    admin: dict = Depends(require_admin)
):
    """Update a user's role (admin only)."""
    result = await auth_service.update_user_role(user_id, role, admin["id"])
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/seed")
async def seed_default_users():
    """Seed default users (for development)."""
    return await auth_service.seed_default_users()


@router.post("/seed-demo")
async def seed_full_demo_data(reset: bool = True):
    """
    Seed comprehensive demo data for Microsoft AI Hackathon.
    
    Hero Scenario: "High-Value Order Recovery & Approval Automation"
    
    This endpoint creates:
    - 4 demo users (admin, manager, operator, viewer)
    - 6 real ERPNext customers
    - 6 sales items with realistic pricing
    - 6-8 sales orders (2+ high-value >50K, 1 delayed, 1 completed)
    - Chat history showing operator creation, manager approval
    - Complete audit trail
    - Dashboard metrics
    
    WARNING: This endpoint is for development/demo purposes only.
    """
    try:
        logger.info("🚀 Starting Microsoft AI Hackathon demo seeding...")
        
        # Import the comprehensive seeding script
        from seed_hackathon_demo import seed_all
        
        # Run all seeding
        result = await seed_all(reset=reset)
        
        return result
    except Exception as e:
        logger.error(f"❌ Error seeding demo data: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Failed to seed demo data: {str(e)}"
        }


@router.post("/reset-demo")
async def reset_demo_data():
    """
    Reset all demo data (clear MongoDB collections).
    WARNING: This deletes all seeded demo data.
    """
    try:
        logger.info("🔄 Resetting demo data...")
        
        from seed_hackathon_demo import reset_demo_data as reset_data
        await reset_data()
        
        return {
            "status": "success",
            "message": "Demo data reset successfully. Data is ready for re-seeding."
        }
    except Exception as e:
        logger.error(f"Error resetting demo data: {e}")
        return {
            "status": "error",
            "message": f"Failed to reset demo data: {str(e)}"
        }


@router.get("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify if token is valid."""
    if user:
        return {"status": "success", "valid": True, "user": user}
    return {"status": "success", "valid": False}
