"""Routes package initialization."""
from routes.chat import router as chat_router
from routes.agent import router as agent_router
from routes.erp import router as erp_router
from routes.entity import router as entity_router

__all__ = ['chat_router', 'agent_router', 'erp_router', 'entity_router']
