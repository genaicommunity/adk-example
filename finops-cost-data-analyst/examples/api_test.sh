#!/bin/bash

# FinOps Cost Data Analyst - API Test Script
# This script demonstrates REST API calls to the agent using curl

set -e

# Configuration
BASE_URL="${ADK_BASE_URL:-http://localhost:8000}"
APP_NAME="finops-cost-data-analyst"
USER_ID="shell-client"
SESSION_ID="session-$(date +%s)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "FinOps Cost Data Analyst - API Test"
echo "============================================================"
echo ""
echo "Base URL: $BASE_URL"
echo "App Name: $APP_NAME"
echo "User ID:  $USER_ID"
echo "Session:  $SESSION_ID"
echo ""

# Function to make API call
query_agent() {
    local question="$1"
    local session="${2:-$SESSION_ID}"

    echo -e "${YELLOW}Question:${NC} $question"
    echo ""

    # Create request payload
    local payload=$(cat <<EOF
{
  "appName": "$APP_NAME",
  "userId": "$USER_ID",
  "sessionId": "$session",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "$question"}]
  }
}
EOF
)

    # Make API call
    local response=$(curl -s -X POST "$BASE_URL/run" \
        -H "Content-Type: application/json" \
        -d "$payload")

    # Check if successful
    if echo "$response" | jq -e '.[0].type == "agent_output"' >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Success${NC}"
        echo ""
        echo -e "${YELLOW}Answer:${NC}"
        echo "$response" | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text'
        echo ""
        return 0
    else
        echo -e "${RED}❌ Error${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        echo ""
        return 1
    fi
}

# Test 1: Check if server is running
echo "============================================================"
echo "Test 1: Check Server Status"
echo "============================================================"
echo ""

if curl -s "$BASE_URL/list-apps" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
    AGENTS=$(curl -s "$BASE_URL/list-apps" | jq -r '.[]')
    echo "Available agents:"
    echo "$AGENTS" | while read -r agent; do
        echo "  - $agent"
    done
else
    echo -e "${RED}❌ Server is not running${NC}"
    echo ""
    echo "Start the server first:"
    echo "  cd /Users/gurukallam/projects/google-adk-agents"
    echo "  adk web --port 8000"
    echo ""
    exit 1
fi
echo ""

# Test 2: Simple cost query
echo "============================================================"
echo "Test 2: Total Cost Query"
echo "============================================================"
echo ""
query_agent "What is the total cost for FY26?"

# Test 3: Top applications
echo "============================================================"
echo "Test 3: Top Applications Query"
echo "============================================================"
echo ""
query_agent "What are the top 5 applications by cost?"

# Test 4: Cloud provider breakdown
echo "============================================================"
echo "Test 4: Cloud Provider Breakdown"
echo "============================================================"
echo ""
query_agent "What is the cost breakdown by cloud provider?"

# Test 5: Average daily cost
echo "============================================================"
echo "Test 5: Average Daily Cost"
echo "============================================================"
echo ""
query_agent "What is the average daily cost?"

# Test 6: Multi-turn conversation
echo "============================================================"
echo "Test 6: Multi-Turn Conversation (Same Session)"
echo "============================================================"
echo ""

CONV_SESSION="conversation-$(date +%s)"
echo "Using session: $CONV_SESSION"
echo ""

echo "--- Turn 1 ---"
query_agent "What are the top 3 applications by cost?" "$CONV_SESSION"

echo "--- Turn 2 (using context from Turn 1) ---"
query_agent "What cloud providers are they using?" "$CONV_SESSION"

# Summary
echo "============================================================"
echo "Tests Complete!"
echo "============================================================"
echo ""
echo "All API tests passed successfully."
echo ""
echo "Next steps:"
echo "  - Review API documentation: docs/API_GUIDE.md"
echo "  - Try Python client: examples/api_client.py"
echo "  - Integrate with your application"
echo ""
