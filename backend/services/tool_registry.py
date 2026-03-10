"""Tool Registry Service - Dynamic custom tools/commands."""
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from database import db

import os


class ToolRegistry:
    """Service for managing custom tools/commands."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TOOLS_FILE = os.path.join(BASE_DIR, "tools_registry.json")
    
    def __init__(self):
        self._ensure_tools_file()
    
    def _ensure_tools_file(self):
        """Ensure tools file exists."""
        if not os.path.exists(self.TOOLS_FILE):
            with open(self.TOOLS_FILE, "w") as f:
                json.dump({"tools": {}}, f)
    
    def _load_tools_from_file(self) -> Dict:
        """Load tools from local JSON file."""
        try:
            with open(self.TOOLS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"tools": {}}
    
    def _save_tools_to_file(self, tools_data: Dict):
        """Save tools to local JSON file."""
        try:
            with open(self.TOOLS_FILE, "w") as f:
                json.dump(tools_data, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Failed to save tools to file: {e}")
    
    async def create_tool(self, tool_name: str, doctype: str, filters: List = None,
                          fields: List[str] = None, description: str = None,
                          limit: int = 20, order_by: str = "creation desc") -> Dict[str, Any]:
        """Create a new custom tool."""
        # Validate tool name
        if not tool_name or not tool_name.replace("_", "").isalnum():
            return {
                "status": "error",
                "message": "Tool name must be alphanumeric (underscores allowed)"
            }
        
        # Check if tool already exists
        existing = await db.custom_tools.find_one({"tool_name": tool_name})
        if existing:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' already exists. Use update_tool to modify."
            }
        
        tool_data = {
            "tool_name": tool_name,
            "doctype": doctype,
            "filters": filters or [],
            "fields": fields,
            "description": description or f"Query {doctype} with custom filters",
            "limit": limit,
            "order_by": order_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "run_count": 0
        }
        
        # Save to MongoDB
        await db.custom_tools.insert_one(tool_data)
        
        # Also save to local file as backup
        tools_file = self._load_tools_from_file()
        tools_file["tools"][tool_name] = tool_data
        self._save_tools_to_file(tools_file)
        
        # Remove MongoDB _id before returning
        tool_data.pop("_id", None)
        
        return {
            "status": "success",
            "message": f"Tool '{tool_name}' created successfully",
            "tool": tool_data
        }
    
    async def get_tool(self, tool_name: str) -> Dict[str, Any]:
        """Get a tool by name."""
        tool = await db.custom_tools.find_one({"tool_name": tool_name}, {"_id": 0})
        
        if not tool:
            # Try loading from file
            tools_file = self._load_tools_from_file()
            tool = tools_file.get("tools", {}).get(tool_name)
        
        if tool:
            return {"status": "success", "tool": tool}
        return {"status": "error", "message": f"Tool '{tool_name}' not found"}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        tools = await db.custom_tools.find({}, {"_id": 0}).to_list(100)
        
        return {
            "status": "success",
            "tools": tools,
            "count": len(tools)
        }
    
    async def update_tool(self, tool_name: str, updates: Dict) -> Dict[str, Any]:
        """Update an existing tool."""
        # Don't allow changing tool_name
        updates.pop("tool_name", None)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.custom_tools.update_one(
            {"tool_name": tool_name},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            return {"status": "error", "message": f"Tool '{tool_name}' not found"}
        
        # Update file backup
        tools_file = self._load_tools_from_file()
        if tool_name in tools_file.get("tools", {}):
            tools_file["tools"][tool_name].update(updates)
            self._save_tools_to_file(tools_file)
        
        return {
            "status": "success",
            "message": f"Tool '{tool_name}' updated successfully"
        }
    
    async def delete_tool(self, tool_name: str) -> Dict[str, Any]:
        """Delete a tool."""
        result = await db.custom_tools.delete_one({"tool_name": tool_name})
        
        if result.deleted_count == 0:
            return {"status": "error", "message": f"Tool '{tool_name}' not found"}
        
        # Remove from file backup
        tools_file = self._load_tools_from_file()
        if tool_name in tools_file.get("tools", {}):
            del tools_file["tools"][tool_name]
            self._save_tools_to_file(tools_file)
        
        return {
            "status": "success",
            "message": f"Tool '{tool_name}' deleted successfully"
        }
    
    async def increment_run_count(self, tool_name: str):
        """Increment the run count for a tool."""
        await db.custom_tools.update_one(
            {"tool_name": tool_name},
            {"$inc": {"run_count": 1}, "$set": {"last_run": datetime.now(timezone.utc).isoformat()}}
        )


# Singleton instance
tool_registry = ToolRegistry()
