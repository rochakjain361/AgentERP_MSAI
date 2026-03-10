# AgentERP - AI-Ready ERP Orchestration Layer

**AgentERP** is a full-stack application that acts as an intelligent orchestration layer between AI agents and ERPNext. It provides a chat-based interface for interacting with ERP systems and serves as a bridge for Azure AI Foundry agents to execute ERP operations.

![AgentERP Architecture](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20MongoDB-blue)
![Status](https://img.shields.io/badge/Status-Demo%20Ready-green)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ with Yarn
- Docker (for MongoDB)
- Git

### Installation & Setup

1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd MS-AgenticAI
```

2. **Set up MongoDB**
```bash
# Run the MongoDB setup script
./setup_mongodb.sh

# This will start a MongoDB container on port 27017
```

3. **Backend Setup**
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables (optional - defaults provided)
# Edit .env file if needed for custom ERPNext credentials
# The .env file already contains demo credentials

# Start the backend server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

4. **Frontend Setup** (in a new terminal)
```bash
cd frontend

# Install dependencies
yarn install

# Start the development server
yarn start
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 🏗️ System Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   React Chat UI     │  ← Modern minimalist interface
│   (Port 3000)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  FastAPI Backend    │  ← AgentERP Orchestration Layer
│  (Port 8000)        │  ← Intent parsing & workflow management
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│     MongoDB         │  ← Chat session persistence
│  (Port 27017)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  ERPNext REST API   │  ← ERP System
│  (External)         │
└─────────────────────┘
```

### Key Components

1. **Chat Interface** (`/frontend/src/components/`)
   - Natural language interaction
   - Real-time ERP status monitoring
   - Visual widgets for ERP data (Sales Orders, Customers)
   - Toast notifications for actions
   - Chat session management

2. **Backend API** (`/backend/server.py`)
   - Intent parsing from natural language
   - ERPNext API wrapper with mock mode
   - Agent orchestration endpoint
   - Chat message persistence
   - Tool registry for dynamic capabilities

3. **ERPNext Service Layer** (`/backend/services/`)
   - Customer management (check, create)
   - Sales Order creation and management
   - Entity operations with AI assistance

4. **AI Integration**
   - GitHub Models (primary - free tier)
   - Azure AI Foundry (fallback - paid)
   - Intent classification and response generation

---

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (configured in `backend/.env`):

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=agenterp

# ERPNext
ERP_URL=https://your-erpnext-instance.com
ERP_API_KEY=your-api-key
ERP_API_SECRET=your-api-secret
ERP_MOCK_MODE=false  # Set to true for demo without ERPNext

# AI - GitHub Models (Free)
GITHUB_TOKEN=your-github-token
AI_ENDPOINT=https://models.inference.ai.azure.com/chat/completions
AI_MODEL=gpt-4o

# AI - Azure AI Foundry (Paid fallback)
AZURE_AI_ENDPOINT=https://your-resource.services.ai.azure.com/models/chat/completions
AZURE_AI_KEY=your-azure-key

# Frontend
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Mock Mode

For development and demos, set `ERP_MOCK_MODE=true` in the `.env` file. This allows the application to run without a real ERPNext instance.

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/
```

### Frontend Tests
```bash
cd frontend
yarn test
```

---

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- `POST /api/chat/sessions` - Create chat session
- `POST /api/chat/messages` - Save chat message
- `POST /api/agent` - Process agent requests
- `GET /api/erp/customers` - List customers
- `POST /api/erp/sales-orders` - Create sales order

---

## 🛠️ Development

### Project Structure
```
MS-AgenticAI/
├── backend/
│   ├── models/          # Pydantic models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── tests/           # Unit tests
│   ├── config.py        # Configuration
│   ├── database.py      # MongoDB connection
│   ├── server.py        # FastAPI app
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── lib/         # Utilities
│   └── package.json     # Node dependencies
├── setup_mongodb.sh     # MongoDB setup script
└── README.md
```

### Adding New Features

1. **Backend**: Add routes in `routes/`, services in `services/`
2. **Frontend**: Add components in `src/components/`
3. **Models**: Define in `backend/models/__init__.py`
4. **Tools**: Register in `backend/tools_registry.json`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🏗️ System Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   React Chat UI     │  ← Modern minimalist interface
│   (Port 3000)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  FastAPI Backend    │  ← AgentERP Orchestration Layer
│  (Port 8001)        │  ← Intent parsing & workflow management
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  ERPNext REST API   │  ← ERP System
│  (External)         │
└─────────────────────┘
```

### Key Components

1. **Chat Interface** (`/frontend/src/components/ChatInterface.js`)
   - Natural language interaction
   - Real-time ERP status monitoring
   - Visual widgets for ERP data (Sales Orders, Customers)
   - Toast notifications for actions

2. **Backend API** (`/backend/server.py`)
   - Intent parsing from natural language
   - ERPNext API wrapper
   - Mock mode for demos
   - Agent orchestration endpoint

3. **ERPNext Service Layer**
   - Customer management (check, create)
   - Sales Order creation
   - Extensible for additional DocTypes

---

## 🔌 ERPNext Integration

### Mock Mode (Current Configuration)

By default, AgentERP runs in **mock mode** for demonstration purposes. This simulates ERPNext responses without requiring a live instance.

**Configuration** (in `/app/backend/.env`):
```bash
ERP_MOCK_MODE="true"
ERP_URL="https://demo.erpnext.com"
ERP_API_KEY="DEMO_KEY"
ERP_API_SECRET="DEMO_SECRET"
```

### Connecting to Real ERPNext

To connect to a live ERPNext instance:

1. **Get API Credentials from ERPNext**
   - Log into your ERPNext instance
   - Go to: User → API Access → Generate Keys
   - Copy the API Key and API Secret

2. **Update Backend Configuration**

Edit `/app/backend/.env`:
```bash
ERP_MOCK_MODE="false"
ERP_URL="https://your-erp-instance.com"
ERP_API_KEY="your_actual_api_key"
ERP_API_SECRET="your_actual_api_secret"
```

3. **Restart Backend**
```bash
sudo supervisorctl restart backend
```

### Setting Up ERPNext Demo Instance

#### Option A: ERPNext Cloud Trial
1. Visit [https://erpnext.com/pricing](https://erpnext.com/pricing)
2. Sign up for a 14-day free trial
3. Once provisioned, generate API keys (User → API Access)
4. Update `.env` with your credentials

#### Option B: Frappe Cloud
1. Visit [https://frappecloud.com](https://frappecloud.com)
2. Create a free developer account
3. Deploy an ERPNext site
4. Generate API credentials
5. Update `.env` with your credentials

#### Option C: Local ERPNext (Advanced)
```bash
# Install Frappe Bench
pip install frappe-bench

# Create new bench
bench init frappe-bench --frappe-branch version-15

# Create new site
cd frappe-bench
bench new-site erp.local

# Install ERPNext
bench get-app erpnext --branch version-15
bench --site erp.local install-app erpnext

# Start server
bench start
```

Then generate API keys from the ERPNext UI and update `.env`.

---

## 📡 API Endpoints

### Agent Orchestration

**POST** `/api/agent`

Main endpoint for AI agent interactions. Accepts structured requests and orchestrates ERPNext operations.

**Request Body:**
```json
{
  "intent": "create_sales_order",
  "customer": "ACME Corp",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 3
    }
  ],
  "transaction_date": "2026-03-06"
}
```

**Supported Intents:**
- `create_sales_order` - Create a new sales order
- `check_customer` - Verify customer exists
- `create_customer` - Create a new customer

**Response:**
```json
{
  "status": "success",
  "message": "Sales Order SO-20260306-A3F2B1 created successfully",
  "data": {
    "name": "SO-20260306-A3F2B1",
    "customer": "ACME Corp",
    "transaction_date": "2026-03-06",
    "items": [...],
    "total_qty": 3,
    "status": "Draft"
  }
}
```

### Direct ERPNext Endpoints

**GET** `/api/customer/{customer_name}`
- Check if a customer exists

**POST** `/api/customer`
- Create a new customer

**POST** `/api/sales-order`
- Create a sales order directly

**GET** `/api/health`
- Health check and ERP status

---

## 🤖 Azure AI Foundry Integration

AgentERP is designed to be called by Azure AI Foundry agents. The `/api/agent` endpoint provides a structured interface for AI agents to execute ERP operations.

### Integration Guide

1. **Configure Azure AI Foundry Agent**

Create a custom action in Azure AI Foundry that calls the AgentERP backend:

```yaml
name: CreateSalesOrder
description: Creates a sales order in ERPNext
endpoint: https://localhost:8000/api/agent
method: POST
headers:
  Content-Type: application/json
body_schema:
  intent: string (required)
  customer: string
  items: array
  transaction_date: string
```

2. **Example Agent Prompt**

```
You are an ERP assistant. When users request ERP operations:

1. Parse the user's request to extract:
   - Intent (create_sales_order, check_customer, etc.)
   - Customer name
   - Items and quantities
   - Transaction date

2. Call the CreateSalesOrder action with structured data

3. Present the response to the user in natural language
```

3. **Sample Agent Code (Python SDK)**

```python
from azure.ai.projects import AIProjectClient

client = AIProjectClient()

# When user says: "Create an order for 5 laptops for TechCorp"
response = client.agents.invoke_action(
    action_name="CreateSalesOrder",
    parameters={
        "intent": "create_sales_order",
        "customer": "TechCorp",
        "items": [{"item_code": "LAPTOP-001", "qty": 5}],
        "transaction_date": "2026-03-06"
    }
)
```

### Security Considerations

When deploying for production use with Azure AI Foundry:

1. **Add Authentication**
   - Implement API key authentication
   - Use Azure AD integration
   - Add rate limiting

2. **Environment Variables**
   - Store credentials in Azure Key Vault
   - Use managed identities

3. **Validation**
   - Validate all inputs
   - Sanitize customer data
   - Implement request size limits

---

## 🎨 User Interface

The AgentERP chat interface features:

- **Modern Minimalist Design** - Swiss design principles with clean typography
- **Real-time ERP Status** - Visual indicator showing connection status
- **Smart Widgets** - Rich display cards for Sales Orders and Customers
- **Natural Language** - Type requests in plain English
- **Responsive Layout** - Works on desktop and mobile

### Example Interactions

Try these in the chat:

```
"Create a sales order for ACME Corp for 3 units of ITEM-001"
"Check customer TechCorp Inc"
"Create a customer named Global Solutions"
```

---

## 🗂️ Project Structure

```
agenterp/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment configuration
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.js    # Main chat component
│   │   ├── App.js                   # Application root
│   │   ├── App.css                  # Custom styles
│   │   └── index.css                # Global styles with design tokens
│   ├── package.json            # Node dependencies
│   └── .env                    # Frontend configuration
│
└── README.md                   # This file
```

---

## 🔧 Development

### Running Locally (Development Mode)

**Backend:**
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```bash
cd frontend
yarn start
```

### Testing API Endpoints

```bash
# Health check
curl https://localhost:8000/api/health

# Create sales order
curl -X POST https://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "create_sales_order",
    "customer": "ACME Corp",
    "items": [{"item_code": "ITEM-001", "qty": 3}],
    "transaction_date": "2026-03-06"
  }'
```

### Adding New ERP Operations

To add support for additional ERPNext DocTypes:

1. **Add to ERPNextService class** (`backend/server.py`):
```python
async def create_invoice(self, invoice: Invoice) -> Dict[str, Any]:
    if self.mock_mode:
        # Mock implementation
        return {"status": "success", ...}
    # Real API call
```

2. **Add intent handler** in `/api/agent` endpoint:
```python
elif request.intent == "create_invoice":
    result = await erp_service.create_invoice(invoice)
    return AgentResponse(...)
```

3. **Update frontend** to handle new widget type if needed

---

## 🚢 Deployment

### Current Deployment

The application is currently deployed on dev platform:
- **URL**: https://localhost:8000
- **Services**: Managed by Supervisor (auto-restart enabled)

### Deploying to Other Platforms

#### Vercel (Frontend)
```bash
cd frontend
vercel deploy
```

#### Railway (Backend)
```bash
cd backend
railway up
```

#### Docker
```dockerfile
# Backend Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 📊 MongoDB Collections

**chat_messages** - Stores chat history
```json
{
  "id": "uuid",
  "role": "user|assistant",
  "content": "message text",
  "type": "text|widget",
  "widget_data": {},
  "timestamp": "ISO datetime"
}
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
ERP_URL="https://your-erp-instance.com"
ERP_API_KEY="your_api_key"
ERP_API_SECRET="your_api_secret"
ERP_MOCK_MODE="true"
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://localhost:8000
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

---

## 📝 Git Initialization

To push this project to GitHub:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AgentERP - AI-Ready ERP Orchestration Layer"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/agenterp.git

# Create main branch and push
git branch -M main
git push -u origin main
```

### Recommended .gitignore

```
# Dependencies
node_modules/
__pycache__/
*.pyc

# Environment variables
.env
.env.local

# Build outputs
build/
dist/

# IDE
.vscode/
.idea/

# Logs
*.log
```

---

## 🎯 Future Enhancements

1. **Additional ERP Operations**
   - Purchase Orders
   - Invoices
   - Inventory Management
   - Reports & Analytics

2. **Authentication & Security**
   - User authentication
   - Role-based access control
   - API key management
   - Audit logging

3. **Advanced AI Features**
   - Multi-turn conversations
   - Context retention
   - Bulk operations
   - Workflow automation

4. **Integrations**
   - Slack notifications
   - Email alerts
   - Webhook support
   - Multiple ERP systems

---

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Restart service
sudo supervisorctl restart backend
```

### Frontend not loading
```bash
# Check logs
tail -n 100 /var/log/supervisor/frontend.err.log

# Restart service
sudo supervisorctl restart frontend
```

### ERPNext connection issues
1. Verify `ERP_MOCK_MODE="true"` for demo mode
2. Check API credentials are correct
3. Ensure ERPNext instance is accessible
4. Verify API keys have proper permissions

---

## 📄 License

MIT License - feel free to use this project for your own ERP integrations.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional ERPNext DocTypes
- Better error handling
- Unit tests
- Performance optimizations
- UI/UX enhancements

---

## 📧 Support

For issues or questions:
- Check the troubleshooting section above
- Review ERPNext API documentation: https://frappeframework.com/docs/v14/user/en/api
- Azure AI Foundry docs: https://learn.microsoft.com/en-us/azure/ai-studio/

---

**Built with ❤️ for the ERP + AI integration hackathon**

**Stack**: FastAPI • React • MongoDB • ERPNext • Azure AI Foundry Ready
