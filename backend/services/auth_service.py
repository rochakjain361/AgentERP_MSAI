"""Authentication Service - User management with company-based filtering."""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

from database import db
from models.enterprise import UserRole, UserCreate, UserResponse

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "agenterp-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and user management with company support."""
    
    @property
    def users_collection(self):
        return db["users"]
    
    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user with optional company association."""
        try:
            existing = await self.users_collection.find_one({"email": user_data.email})
            if existing:
                return {"status": "error", "message": "Email already registered"}
            
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name,
                "password_hash": self._hash_password(user_data.password),
                "role": user_data.role.value,
                "company": user_data.company,  # Associated company/customer
                "created_at": datetime.now(timezone.utc),
                "last_login": None,
                "is_active": True
            }
            
            await self.users_collection.insert_one(user_doc)
            
            token = self._create_access_token({
                "sub": user_id,
                "email": user_data.email,
                "role": user_data.role.value,
                "company": user_data.company
            })
            
            logger.info(f"User registered: {user_data.email} with role {user_data.role.value}, company: {user_data.company}")
            
            return {
                "status": "success",
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": user_data.email,
                    "name": user_data.name,
                    "role": user_data.role.value,
                    "company": user_data.company,
                    "created_at": user_doc["created_at"].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return token with company info. Creates demo users if they don't exist."""
        try:
            user = await self.users_collection.find_one({"email": email})
            
            # If user doesn't exist and it's a demo user, create it
            demo_users = {
                "admin@agenterp.com": {"name": "Admin User", "password": "admin123", "role": UserRole.ADMIN, "company": None},
                "manager@agenterp.com": {"name": "Sarah Johnson", "password": "manager123", "role": UserRole.MANAGER, "company": "TechCorp Solutions"},
                "operator@agenterp.com": {"name": "Raj Patel", "password": "operator123", "role": UserRole.OPERATOR, "company": "TechCorp Solutions"},
                "viewer@agenterp.com": {"name": "Lisa Chen", "password": "viewer123", "role": UserRole.VIEWER, "company": "TechCorp Solutions"},
                "manager@techcorp.com": {"name": "TechCorp Manager", "password": "manager123", "role": UserRole.MANAGER, "company": "TechCorp Solutions"},
                "operator@innovate.com": {"name": "InnovateTech Operator", "password": "operator123", "role": UserRole.OPERATOR, "company": "InnovateTech Pvt Ltd"},
                "viewer@global.com": {"name": "Global Viewer", "password": "viewer123", "role": UserRole.VIEWER, "company": "Global Industries Ltd"},
            }
            if not user and email in demo_users:
                # Create a copy to avoid mutating the demo_users dict
                user_data = {**demo_users[email], "email": email}
                result = await self.register_user(UserCreate(**user_data))
                if result["status"] == "success":
                    user = await self.users_collection.find_one({"email": email})
                    logger.info(f"Created demo user: {email}")
            
            if not user:
                return {"status": "error", "message": "Invalid email or password"}
            
            if not self._verify_password(password, user["password_hash"]):
                return {"status": "error", "message": "Invalid email or password"}
            
            await self.users_collection.update_one(
                {"id": user["id"]},
                {"$set": {"last_login": datetime.now(timezone.utc)}}
            )
            
            token = self._create_access_token({
                "sub": user["id"],
                "email": user["email"],
                "role": user["role"],
                "company": user.get("company")
            })
            
            logger.info(f"User logged in: {email}")
            
            return {
                "status": "success",
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "company": user.get("company"),
                    "created_at": user["created_at"].isoformat(),
                    "last_login": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data including company."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return None
            
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "company": user.get("company")
            }
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = await self.users_collection.find_one({"id": user_id})
        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "company": user.get("company"),
                "created_at": user["created_at"].isoformat()
            }
        return None
    
    async def update_user_role(self, user_id: str, new_role: UserRole, admin_id: str) -> Dict[str, Any]:
        try:
            admin = await self.users_collection.find_one({"id": admin_id})
            if not admin or admin["role"] != "admin":
                return {"status": "error", "message": "Only admins can change roles"}
            
            result = await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {"role": new_role.value}}
            )
            
            if result.modified_count > 0:
                return {"status": "success", "message": f"Role updated to {new_role.value}"}
            return {"status": "error", "message": "User not found"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def update_user_company(self, user_id: str, company: str, admin_id: str) -> Dict[str, Any]:
        """Update user's company association (admin only)."""
        try:
            admin = await self.users_collection.find_one({"id": admin_id})
            if not admin or admin["role"] != "admin":
                return {"status": "error", "message": "Only admins can assign companies"}
            
            result = await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {"company": company}}
            )
            
            if result.modified_count > 0:
                return {"status": "success", "message": f"Company updated to {company}"}
            return {"status": "error", "message": "User not found"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def list_users(self) -> Dict[str, Any]:
        try:
            users = []
            cursor = self.users_collection.find({}, {"password_hash": 0, "_id": 0})
            async for user in cursor:
                user["created_at"] = user["created_at"].isoformat() if user.get("created_at") else None
                user["last_login"] = user["last_login"].isoformat() if user.get("last_login") else None
                users.append(user)
            
            return {"status": "success", "users": users, "count": len(users)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def seed_default_users(self) -> Dict[str, Any]:
        """Seed default demo users with proper roles."""
        try:
            count = await self.users_collection.count_documents({})
            if count > 0:
                return {"status": "info", "message": "Users already exist"}
            
            # Demo users for role-based access control
            default_users = [
                {"email": "admin@agenterp.com", "name": "Admin User", "password": "admin123", "role": UserRole.ADMIN, "company": None},
                {"email": "manager@agenterp.com", "name": "Manager - Approvals", "password": "manager123", "role": UserRole.MANAGER, "company": "TechCorp Solutions"},
                {"email": "operator@agenterp.com", "name": "Operator - Order Creator", "password": "operator123", "role": UserRole.OPERATOR, "company": "TechCorp Solutions"},
                {"email": "viewer@agenterp.com", "name": "Viewer - Read Only", "password": "viewer123", "role": UserRole.VIEWER, "company": "TechCorp Solutions"},
            ]
            
            for user in default_users:
                await self.register_user(UserCreate(**user))
            
            logger.info("Default users seeded for demo RBAC scenario")
            return {
                "status": "success", 
                "message": "Demo users created successfully",
                "users": [{"email": u["email"], "role": u["role"].value} for u in default_users]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
auth_service = AuthService()
