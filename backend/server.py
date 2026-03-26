"""AgentERP - AI-powered ERP Orchestration Layer.

This is the main FastAPI application that provides:
- AI-powered chat interface for natural language ERP operations
- Direct ERPNext API integration
- Chat session persistence with MongoDB
- Role-based access control (RBAC)
- Approval workflows
- Audit trail logging
- Proactive insights engine
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging
import os

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes
from routes.chat import router as chat_router
from routes.agent import router as agent_router
from routes.erp import router as erp_router
from routes.entity import router as entity_router
from routes.tools import router as tools_router
from routes.auth import router as auth_router
from routes.audit import router as audit_router
from routes.approvals import router as approvals_router
from routes.insights import router as insights_router
from routes.reasoning import router as reasoning_router
from routes.intelligence import router as intelligence_router
from routes.ai_analysis import router as ai_analysis_router
from database import close_db
from config import CORS_ORIGINS

# Create FastAPI app
app = FastAPI(
    title="AgentERP",
    description="AI-powered ERP Orchestration Layer for ERPNext - Enterprise Edition",
    version="2.0.0"
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(erp_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(entity_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(approvals_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(reasoning_router, prefix="/api")
app.include_router(intelligence_router, prefix="/api")
app.include_router(ai_analysis_router, prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("AgentERP Enterprise starting up...")
    # Seed default users on startup
    from services.auth_service import auth_service
    await auth_service.seed_default_users()
    logger.info("AgentERP Enterprise ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
