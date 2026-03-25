#!/usr/bin/env bash

# Quick Start: Microsoft AI Hackathon Demo Setup
# This script gets AgentERP running with the demo scenario in under 5 minutes

set -e

echo "🚀 AgentERP Hackathon Demo Quick Start"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "backend/server.py" ]; then
    echo "❌ Please run this script from the root of the AgentERP project"
    exit 1
fi

echo -e "${BLUE}Step 1: Starting Backend Server${NC}"
echo "Commands:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn server:app --host 0.0.0.0 --port 8001"
echo ""
echo "💡 Run in a new terminal and wait for 'Application startup complete'"
read -p "Press Enter once backend is running (port 8001)..."
echo ""

echo -e "${BLUE}Step 2: Seeding Demo Data${NC}"
echo "Running: curl -X POST http://localhost:8001/api/auth/seed-demo"
echo ""

# Run seed endpoint
SEED_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/seed-demo)
echo "$SEED_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SEED_RESPONSE"
echo ""

echo -e "${GREEN}✅ Backend ready with demo data!${NC}"
echo ""

echo -e "${BLUE}Step 3: Starting Frontend${NC}"
echo "Commands:"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "💡 Run in a new terminal and wait for 'On Your Network' message"
read -p "Press Enter once frontend is running (port 3000)..."
echo ""

echo -e "${GREEN}✅ Demo Setup Complete!${NC}"
echo ""
echo "🎯 Demo is Live:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend: http://localhost:8001"
echo ""
echo "👤 Demo Users:"
echo "   Admin:    admin@agenterp.com / admin123"
echo "   Manager:  manager@agenterp.com / manager123"
echo "   Operator: operator@agenterp.com / operator123"
echo "   Viewer:   viewer@agenterp.com / viewer123"
echo ""
echo "📖 Demo Scenario:"
echo "   1. Login as 'operator' → view pending orders"
echo "   2. Switch to 'manager' via role selector"
echo "   3. Review high-value orders (>₹50,000) in Approvals panel"
echo "   4. Approve orders and watch audit log update in real-time"
echo "   5. View dashboard metrics reflecting approved orders"
echo ""
echo "💬 Try These Commands:"
echo "   - 'Show me pending approvals'"
echo "   - 'Which high-value orders are stuck?'"
echo "   - 'Approve order SO-2024-00101'"
echo "   - 'Show me audit log for this order'"
echo ""
