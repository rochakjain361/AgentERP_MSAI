# AgentERP - AI ERP Orchestration Layer

## Original Problem Statement
Build an AI-ready ERP orchestration layer called AgentERP that integrates with ERPNext using its official REST APIs. The project acts as an orchestration layer between AI agents and ERPNext.

## User Personas
- **Business Users**: Need to interact with ERP data using natural language
- **Azure AI Foundry Agents**: Will call this backend (future integration)
- **ERP Administrators**: Need quick insights and analytics from ERPNext

## Core Requirements
1. Natural language interface to ERPNext operations
2. Multi-chat system with persistent sessions
3. Real-time connection to live ERPNext instance
4. Comprehensive business analytics dashboard
5. Direct links to ERPNext for detailed views

## Technology Stack
- **Backend**: FastAPI (Python), httpx for HTTP calls
- **Frontend**: React.js, TailwindCSS, shadcn/ui components
- **Database**: MongoDB for chat session persistence
- **AI**: GitHub Models (GPT-4o) for natural language understanding
- **ERP**: Live ERPNext instance (india-next.m.frappe.cloud)

## Architecture
```
User → React Chat UI → FastAPI Backend → ERPNext REST API → ERPNext System
                            ↓
                      GitHub AI Models (intent parsing)
                            ↓
                      MongoDB (session storage)
```

## What's Been Implemented

### Phase 1: Core Infrastructure ✅
- FastAPI backend with CORS middleware
- ERPNext service layer with token authentication
- MongoDB integration for chat persistence
- Health check and status endpoints

### Phase 2: AI Integration ✅
- GitHub Models integration (GPT-4o)
- Natural language intent parsing
- Sales order creation with all required fields
- Customer lookup and creation

### Phase 3: Chat System ✅
- Multi-session chat like ChatGPT
- Session persistence in MongoDB
- Chat history loading
- Session deletion

### Phase 4: UI/UX Enhancements ✅
- Interactive sidebar with quick actions
- Command palette (⌘K)
- Smart context-aware suggestions
- Direct ERPNext links in header and widgets

### Phase 5: Comprehensive Analytics Dashboard ✅ (December 2026)
- **KPI Cards**: Total Sales, Customers, Invoiced, Outstanding
- **Sales by Status**: Breakdown of orders by status with values
- **Top Customers by Revenue**: Ranked table with order counts
- **Items Catalog**: Full item listing with groups
- **Recent Orders Table**: With links to ERPNext
- **Recent Invoices Table**: With outstanding amounts highlighted
- **Quick Links**: Direct links to ERPNext reports

### Bug Fixes ✅
- Fixed MongoDB ObjectId serialization in create_chat_session
- Fixed Sales Order creation (added currency, price list, warehouse fields)
- Added direct pattern matching for analytics to bypass AI rate limits

### Phase 6: Generic ERP Entity Engine ✅ (March 2026)
- **Generic CRUD**: Create, Read, Update, Delete for any ERPNext DocType
- **Query Engine**: Filter and query any DocType with custom fields
- **Validation**: Automatic validation of required fields and related entities
- **Interactive Creation**: Guided field collection for missing data
- **Dynamic Tool Registry**: Create and run custom saved queries/tools

## Key API Endpoints

### Chat & AI
- `POST /api/chat` - AI-powered chat with intent parsing
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions` - List all sessions
- `GET /api/chat/messages/{session_id}` - Get session messages
- `DELETE /api/chat/sessions/{session_id}` - Delete session
- `GET /api/health` - Health check

### Generic Entity Engine
- `POST /api/entity` - Generic CRUD (actions: create, read, update, delete, query, validate, exists, meta)
- `POST /api/entity/interactive-create` - Interactive creation with field guidance
- `POST /api/entity/tool` - Tool registry (actions: create_tool, run_tool, list_tools, update_tool, delete_tool)
- `GET /api/entity/doctypes` - List common ERPNext DocTypes
- `GET /api/entity/meta/{doctype}` - Get DocType metadata

## Database Schema
```javascript
// chat_sessions collection
{
  "id": "uuid",
  "title": "Chat title",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "message_count": 0
}

// chat_messages collection
{
  "id": "uuid",
  "session_id": "uuid",
  "role": "user|assistant",
  "content": "message text",
  "type": "text|widget",
  "widget_data": {},
  "timestamp": "ISO datetime"
}
```

## Environment Variables
- `ERP_URL` - ERPNext instance URL
- `ERP_API_KEY` - ERPNext API key
- `ERP_API_SECRET` - ERPNext API secret
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - MongoDB database name
- `GITHUB_TOKEN` - GitHub AI API token
- `AI_ENDPOINT` - AI API endpoint
- `AI_MODEL` - AI model name (gpt-4o)

## AI Service Configuration

### Primary: GitHub Models
- Endpoint: `https://models.inference.ai.azure.com/chat/completions`
- Model: `gpt-4o`
- Authentication: Bearer token

### Fallback: Azure AI Foundry (Phi-4)
- Endpoint: `https://sample-erp-resource.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview`
- Model: `Phi-4` (cost-efficient, deployed on user's Azure)
- Authentication: API key header

### Cost Optimization
- Reduced conversation history from 6 to 4 messages
- Reduced max_tokens from 500 to 300
- Lower temperature (0.5) for more consistent responses
- Direct pattern matching bypasses AI for analytics/dashboard requests

## Prioritized Backlog

### P0 - Completed
- ✅ New Chat button creates sessions directly
- ✅ Comprehensive analytics dashboard with tables
- ✅ Code refactoring - Backend and Frontend modularization
- ✅ Custom Tool Builder UI (March 2026)
- ✅ AI Service Fallback (GitHub Models → Azure AI Foundry)
- ✅ Sanity check verification - all tests passed

### P1 - Next Up
- [ ] Generic Entity Browser UI - dedicated UI to browse/manage any ERPNext DocType
- [ ] Integrate Tool Execution into AI Chat - make AI recognize saved tools
- [ ] Add unit tests for backend services

### P2 - Future
- [ ] Enhanced API Documentation (Swagger/Markdown)
- [ ] Azure AI Foundry agent integration
- [ ] Voice input support
- [ ] Export dashboard as PDF
- [ ] Custom date range for analytics
- [ ] Real-time notifications for ERP events

## Refactored Code Structure (March 2026)

### Backend Structure
```
/app/backend/
├── server.py          # Main FastAPI app (~60 lines)
├── config.py          # Environment configuration
├── database.py        # MongoDB connection
├── models/
│   └── __init__.py    # All Pydantic models
├── services/
│   ├── __init__.py
│   ├── erp_service.py # ERPNext API integration
│   └── ai_service.py  # GPT-4o integration
├── routes/
│   ├── __init__.py
│   ├── chat.py        # Chat session endpoints
│   ├── agent.py       # AI chat endpoints
│   └── erp.py         # Direct ERP endpoints
└── tests/
    └── test_agenterp_api.py
```

### Frontend Structure
```
/app/frontend/src/
├── components/
│   ├── ChatInterface.js  # Main component (~270 lines)
│   ├── Sidebar.js        # Navigation sidebar
│   ├── ChatSidebar.js    # Chat history sidebar
│   ├── CommandPalette.js # ⌘K command palette
│   ├── ChatMessages.js   # Message display
│   ├── ChatInput.js      # Message input
│   ├── SmartSuggestions.js
│   ├── ERPWidgets.js     # ERP data widgets
│   └── DashboardView.js  # Analytics dashboard
├── hooks/
│   ├── useChat.js        # Chat state management
│   └── useHealth.js      # Health check hook
└── lib/
    ├── api.js            # API client
    └── constants.js      # App constants
```

## Known Limitations
- GitHub AI API has rate limits (429 errors) - mitigated with direct pattern matching and Azure AI Foundry fallback
- ERPNext API may timeout on large data requests

## Verification Status (March 2026)
- **Backend**: 100% (25/25 tests passed)
- **Frontend**: 100% (all features verified)
- **Custom Tool Builder**: ✅ Working (create, list, run, delete tools)
- **Analytics Dashboard**: ✅ Working (KPIs, tables, quick links)
- **AI Chat**: ✅ Working (with fallback mechanism)
- **Error Status**: No "Response body is already used" error (was browser extension issue)

## Test Reports
- `/app/test_reports/iteration_4.json` - Latest sanity check (all passed)
- `/app/backend/tests/test_agenterp_api.py` - 12 backend tests
- `/app/backend/tests/test_tool_builder.py` - 13 tool builder tests
