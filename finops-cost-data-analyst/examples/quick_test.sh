#!/bin/bash
# Quick Test - Demonstrates the working session creation + query flow

set -e

BASE_URL="http://localhost:8000"
APP_NAME="finops-cost-data-analyst"
USER_ID="quick-test-user"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================"
echo "FinOps Agent - Quick Test (With Session Creation)"
echo "============================================================"
echo ""

# Step 1: Create session
echo -e "${YELLOW}Step 1: Creating session...${NC}"
echo '{}' > /tmp/empty.json
SESSION_RESPONSE=$(curl -s -X POST \
    "$BASE_URL/apps/$APP_NAME/users/$USER_ID/sessions" \
    -H "Content-Type: application/json" \
    -d @/tmp/empty.json)

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.id')

echo -e "${GREEN}✅ Session created: $SESSION_ID${NC}"
echo ""

# Step 2: Query agent
echo -e "${YELLOW}Step 2: Querying agent...${NC}"
echo "Question: What is the total cost for FY26?"
echo ""

cat > /tmp/query.json <<EOF
{
  "appName": "$APP_NAME",
  "userId": "$USER_ID",
  "sessionId": "$SESSION_ID",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "What is the total cost for FY26?"}]
  }
}
EOF

RESPONSE=$(curl -s -X POST "$BASE_URL/run" \
    -H "Content-Type: application/json" \
    -d @/tmp/query.json)

# Extract answer
if echo "$RESPONSE" | jq -e '.[0].type == "agent_output"' >/dev/null 2>&1; then
    ANSWER=$(echo "$RESPONSE" | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text')
    echo -e "${GREEN}✅ Success!${NC}"
    echo ""
    echo -e "${YELLOW}Answer:${NC}"
    echo "$ANSWER"
    echo ""
else
    echo -e "${RED}❌ Error${NC}"
    echo "$RESPONSE" | jq '.'
fi

echo "============================================================"
echo "Test Complete!"
echo "============================================================"
