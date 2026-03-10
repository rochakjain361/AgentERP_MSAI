# Azure AI Foundry Integration Guide

This guide explains how to integrate AgentERP with Azure AI Foundry agents to create an AI-powered ERP assistant.

## Overview

AgentERP provides a REST API endpoint (`/api/agent`) that Azure AI Foundry agents can call to execute ERP operations in ERPNext. The agent acts as the "brain" that understands user intent, while AgentERP acts as the "hands" that execute operations.

## Architecture

```
┌──────────────┐
│   End User   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Azure AI Foundry    │  ← Natural Language Understanding
│      Agent           │  ← Intent Recognition
└──────┬───────────────┘
       │ REST API Call
       ▼
┌──────────────────────┐
│    AgentERP API      │  ← Intent → Action Translation
│   /api/agent         │  ← Business Logic
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   ERPNext System     │  ← ERP Operations
└──────────────────────┘
```

---

## Step 1: Create Azure AI Foundry Project

1. **Sign in to Azure AI Foundry**
   - Visit: https://ai.azure.com
   - Sign in with your Microsoft account

2. **Create a New Project**
   ```
   Project Name: AgentERP Assistant
   Description: AI agent for ERP operations
   Region: Select your preferred region
   ```

3. **Configure Resources**
   - Create or link an Azure OpenAI resource
   - Enable Function Calling capabilities

---

## Step 2: Configure AgentERP API as a Function

Azure AI Foundry agents use "functions" (also called "tools" or "actions") to interact with external systems.

### Function Definition

Create a function in your Azure AI Foundry project with the following configuration:

**Function Name:** `execute_erp_operation`

**Description:**
```
Executes ERP operations in ERPNext including creating sales orders, 
managing customers, and checking data. Use this function when users 
request ERP-related actions.
```

**API Configuration:**
```yaml
endpoint: https://localhost:8000/api/agent
method: POST
headers:
  Content-Type: application/json
```

**Parameters Schema:**
```json
{
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["create_sales_order", "check_customer", "create_customer"],
      "description": "The type of ERP operation to perform"
    },
    "customer": {
      "type": "string",
      "description": "Customer name (required for all operations)"
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "item_code": {"type": "string"},
          "qty": {"type": "integer"}
        }
      },
      "description": "List of items (required for create_sales_order)"
    },
    "transaction_date": {
      "type": "string",
      "format": "date",
      "description": "Transaction date in YYYY-MM-DD format"
    },
    "customer_data": {
      "type": "object",
      "properties": {
        "customer_name": {"type": "string"},
        "customer_type": {"type": "string"},
        "territory": {"type": "string"}
      },
      "description": "Customer details (required for create_customer)"
    }
  },
  "required": ["intent"]
}
```

---

## Step 3: Create the Agent

### Agent Instructions

Configure your agent with these instructions:

```
You are an ERP Assistant that helps users manage their ERPNext system through 
natural language. You can create sales orders, manage customers, and retrieve 
information.

CAPABILITIES:
- Create sales orders for customers
- Check if customers exist in the system
- Create new customer records

WORKFLOW:
1. Understand the user's request
2. Extract key information:
   - Customer name
   - Items and quantities
   - Dates
3. Call the execute_erp_operation function with the appropriate intent
4. Present the results to the user in a friendly manner

IMPORTANT RULES:
- Always confirm customer name before creating orders
- Use today's date if no date is specified
- For new customers, ask for customer type and territory if not provided
- Present ERP data clearly and concisely

EXAMPLES:

User: "Create a sales order for ACME Corp for 5 laptops"
You should:
1. Extract: customer="ACME Corp", items=[{item_code: "LAPTOP-001", qty: 5}]
2. Call: execute_erp_operation with intent="create_sales_order"
3. Respond: "I've created sales order SO-XXXXX for ACME Corp with 5 laptops."

User: "Check if TechCorp exists in our system"
You should:
1. Extract: customer="TechCorp"
2. Call: execute_erp_operation with intent="check_customer"
3. Respond: "Yes, TechCorp exists in our system" or "No, TechCorp is not found"
```

### Agent Configuration

```yaml
name: AgentERP Assistant
model: gpt-4-turbo-2024-04-09
temperature: 0.3
max_tokens: 1000
functions:
  - execute_erp_operation
```

---

## Step 4: Test the Integration

### Test Case 1: Create Sales Order

**User Input:**
```
Create a sales order for ACME Corp for 3 units of ITEM-001
```

**Expected Agent Behavior:**
1. Parse the request
2. Call function with:
```json
{
  "intent": "create_sales_order",
  "customer": "ACME Corp",
  "items": [{"item_code": "ITEM-001", "qty": 3}],
  "transaction_date": "2026-03-06"
}
```
3. Receive response and present to user

**Expected Output:**
```
I've created a sales order for ACME Corp:
- Order Number: SO-20260306-A3F2B1
- Items: 3 units of ITEM-001
- Date: 2026-03-06
- Status: Draft

The order is ready for processing!
```

### Test Case 2: Check Customer

**User Input:**
```
Does TechCorp Inc exist in our database?
```

**Expected Agent Behavior:**
1. Call function with:
```json
{
  "intent": "check_customer",
  "customer": "TechCorp Inc"
}
```
2. Interpret response

**Expected Output:**
```
Yes, TechCorp Inc exists in your system:
- Type: Company
- Territory: India
```

---

## Step 5: Python SDK Integration

If you're building a custom application using the Azure AI Projects SDK:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize client
credential = DefaultAzureCredential()
client = AIProjectClient(
    credential=credential,
    subscription_id="your-subscription-id",
    resource_group_name="your-resource-group",
    project_name="AgentERP Assistant"
)

# Create agent with function
agent = client.agents.create_agent(
    model="gpt-4-turbo",
    name="ERP Assistant",
    instructions="You are an ERP assistant...",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "execute_erp_operation",
                "description": "Executes ERP operations",
                "parameters": {
                    # ... schema from above
                }
            }
        }
    ]
)

# Create thread and run
thread = client.agents.create_thread()

message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Create a sales order for ACME Corp for 5 units of ITEM-001"
)

run = client.agents.create_run(
    thread_id=thread.id,
    agent_id=agent.id
)

# Handle function calls
while run.status in ["queued", "in_progress", "requires_action"]:
    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        
        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call.function.name == "execute_erp_operation":
                # Call AgentERP API
                import requests
                response = requests.post(
                    "https://localhost:8000/api/agent",
                    json=json.loads(tool_call.function.arguments),
                    headers={"Content-Type": "application/json"}
                )
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(response.json())
                })
        
        # Submit tool outputs
        run = client.agents.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    
    # Wait and check status
    time.sleep(1)
    run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

# Get messages
messages = client.agents.list_messages(thread_id=thread.id)
for message in messages.data:
    if message.role == "assistant":
        print(f"Assistant: {message.content[0].text.value}")
```

---

## Step 6: Deploy to Production

### Security Enhancements

Before deploying to production, implement these security measures:

1. **API Authentication**
```python
# Add to backend/server.py
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    api_key = credentials.credentials
    if api_key != os.environ.get("AGENT_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key

@api_router.post("/agent", response_model=AgentResponse)
async def agent_orchestration(
    request: AgentRequest, 
    api_key: str = Depends(verify_api_key)
):
    # ... existing code
```

2. **Update Azure Function Configuration**
```yaml
endpoint: https://your-production-domain.com/api/agent
method: POST
headers:
  Content-Type: application/json
  Authorization: Bearer YOUR_SECRET_API_KEY
```

3. **Rate Limiting**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@api_router.post("/agent")
@limiter.limit("10/minute")
async def agent_orchestration(request: AgentRequest):
    # ... existing code
```

### Environment Configuration

Production `.env` configuration:
```bash
# AgentERP Backend
ERP_URL="https://your-production-erp.com"
ERP_API_KEY="your_production_api_key"
ERP_API_SECRET="your_production_api_secret"
ERP_MOCK_MODE="false"
AGENT_API_KEY="generate_a_secure_random_key"
```

---

## Step 7: Monitoring and Logging

### Enable Logging

```python
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor
configure_azure_monitor(
    connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
)

logger = logging.getLogger(__name__)

@api_router.post("/agent")
async def agent_orchestration(request: AgentRequest):
    logger.info(f"Agent request received: {request.intent}")
    try:
        # ... existing code
        logger.info(f"Agent request completed successfully: {request.intent}")
    except Exception as e:
        logger.error(f"Agent request failed: {str(e)}", exc_info=True)
        raise
```

### Monitor in Azure

1. Go to Azure Portal
2. Navigate to Application Insights
3. View metrics:
   - Request rate
   - Response time
   - Failure rate
   - Custom events

---

## Troubleshooting

### Common Issues

**Issue: Function not being called**
- Verify the function schema matches the API endpoint
- Check agent instructions mention when to use the function
- Review function description clarity

**Issue: Invalid parameters**
- Add parameter validation in agent instructions
- Test with various user inputs
- Log function calls for debugging

**Issue: Timeout errors**
- Increase timeout in Azure function configuration
- Optimize ERPNext API calls
- Add retry logic

**Issue: Authentication failures**
- Verify API keys are correct
- Check header format
- Ensure credentials are not expired

---

## Advanced Features

### Multi-turn Conversations

Enable context retention:

```python
# Store conversation context in MongoDB
@api_router.post("/agent")
async def agent_orchestration(
    request: AgentRequest,
    conversation_id: Optional[str] = None
):
    if conversation_id:
        # Retrieve previous context
        context = await db.conversations.find_one({"id": conversation_id})
    
    # Process request with context
    # ...
    
    # Save updated context
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"last_action": request.intent, "timestamp": datetime.now()}},
        upsert=True
    )
```

### Bulk Operations

Support batch processing:

```python
class BulkAgentRequest(BaseModel):
    operations: List[AgentRequest]

@api_router.post("/agent/bulk")
async def bulk_agent_orchestration(request: BulkAgentRequest):
    results = []
    for operation in request.operations:
        result = await process_single_operation(operation)
        results.append(result)
    return {"status": "success", "results": results}
```

---

## Cost Optimization

### Tips for Reducing Azure Costs

1. **Use Appropriate Models**
   - GPT-4 Turbo for complex reasoning
   - GPT-3.5 Turbo for simple operations

2. **Optimize Token Usage**
   - Keep instructions concise
   - Use function descriptions effectively
   - Limit response length

3. **Cache Common Queries**
   - Cache customer lookups
   - Store frequently accessed data
   - Implement request deduplication

---

## Support and Resources

- **AgentERP Documentation**: See main README.md
- **Azure AI Foundry Docs**: https://learn.microsoft.com/en-us/azure/ai-studio/
- **ERPNext API Docs**: https://frappeframework.com/docs/v14/user/en/api
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling

---

## Next Steps

1. Set up Azure AI Foundry project
2. Configure the function following this guide
3. Test with sample queries
4. Deploy to production with security enabled
5. Monitor performance and optimize

Ready to revolutionize your ERP workflow with AI! 🚀
