"""Audit Service - Tracks all actions with full context."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import logging

from database import db
from models.enterprise import AuditAction, AuditLogCreate, UserRole

logger = logging.getLogger(__name__)


class AuditService:
    """Service for tracking and logging all system actions."""
    
    @property
    def audit_collection(self):
        return db["audit_logs"]
    
    async def log_action(
        self,
        user_id: str,
        user_email: str,
        user_role: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        input_params: Optional[dict] = None,
        result: str = "success",
        result_message: Optional[str] = None,
        ai_reasoning: Optional[str] = None,
        approval_required: bool = False,
        approval_id: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log an action to the audit trail with company context."""
        try:
            log_id = str(uuid.uuid4())
            log_entry = {
                "id": log_id,
                "user_id": user_id,
                "user_email": user_email,
                "user_role": user_role,
                "company": company,  # Company for data segregation
                "action": action.value if isinstance(action, AuditAction) else action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "input_params": input_params,
                "result": result,
                "result_message": result_message,
                "ai_reasoning": ai_reasoning,
                "approval_required": approval_required,
                "approval_id": approval_id,
                "timestamp": datetime.now(timezone.utc)
            }
            
            await self.audit_collection.insert_one(log_entry)
            logger.info(f"Audit logged: {action} by {user_email} on {resource_type}")
            
            return {"status": "success", "log_id": log_id}
            
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_logs(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit logs with filtering."""
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            if action:
                query["action"] = action
            if resource_type:
                query["resource_type"] = resource_type
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            cursor = self.audit_collection.find(
                query, 
                {"_id": 0}
            ).sort("timestamp", -1).skip(offset).limit(limit)
            
            logs = []
            async for log in cursor:
                log["timestamp"] = log["timestamp"].isoformat()
                logs.append(log)
            
            total = await self.audit_collection.count_documents(query)
            
            return {
                "status": "success",
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error fetching audit logs: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get activity summary for a user."""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "last_occurrence": {"$max": "$timestamp"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            cursor = self.audit_collection.aggregate(pipeline)
            actions = []
            async for doc in cursor:
                doc["last_occurrence"] = doc["last_occurrence"].isoformat()
                actions.append(doc)
            
            return {"status": "success", "user_id": user_id, "activity_summary": actions}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_action_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get count of actions for business impact calculation."""
        try:
            now = datetime.now(timezone.utc)
            
            # Today's actions
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = await self.audit_collection.count_documents({
                "timestamp": {"$gte": today_start}
            })
            
            # This month's actions
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_count = await self.audit_collection.count_documents({
                "timestamp": {"$gte": month_start}
            })
            
            return {
                "status": "success",
                "today": today_count,
                "this_month": month_count
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_recent_activity(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent activity for dashboard."""
        return await self.get_logs(limit=limit)


# Singleton instance
audit_service = AuditService()
