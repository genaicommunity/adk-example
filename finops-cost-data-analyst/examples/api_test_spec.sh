#!/bin/bash

# FinOps Cost Data Analyst - Spec-Driven API Test Script
# This script uses agent-card.json and a2a-spec.json for testing

set -e

# Configuration
BASE_URL="${ADK_BASE_URL:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
AGENT_CARD="$AGENT_DIR/agent-card.json"
A2A_SPEC="$AGENT_DIR/a2a-spec.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo "FinOps Cost Data Analyst - Spec-Driven API Test"
echo "============================================================"
echo ""
echo "Base URL:     $BASE_URL"
echo "Agent Card:   $AGENT_CARD"
echo "A2A Spec:     $A2A_SPEC"
echo ""

# Check if spec files exist
if [ ! -f "$AGENT_CARD" ]; then
    echo -e "${RED}❌ Error: agent-card.json not found at $AGENT_CARD${NC}"
    exit 1
fi

if [ ! -f "$A2A_SPEC" ]; then
    echo -e "${RED}❌ Error: a2a-spec.json not found at $A2A_SPEC${NC}"
    exit 1
fi

# Load agent metadata from spec
echo "============================================================"
echo "Loading Agent Specification"
echo "============================================================"
echo ""

APP_NAME=$(jq -r '.agentCard.metadata.name' "$AGENT_CARD")
DISPLAY_NAME=$(jq -r '.agentCard.metadata.displayName' "$AGENT_CARD")
VERSION=$(jq -r '.agentCard.metadata.version' "$AGENT_CARD")

echo -e "${GREEN}✅ Loaded Agent Spec${NC}"
echo "   Name:    $APP_NAME"
echo "   Display: $DISPLAY_NAME"
echo "   Version: $VERSION"
echo ""

# Show capabilities
echo "📋 Capabilities:"
jq -r '.agentCard.capabilities.primary[]' "$AGENT_CARD" | while read -r cap; do
    echo "   - $cap"
done
echo ""

# Show intents
echo "🎯 Supported Intents:"
jq -r '.agentCard.intents | keys[]' "$AGENT_CARD" | while read -r intent; do
    description=$(jq -r ".agentCard.intents.\"$intent\".description" "$AGENT_CARD")
    echo "   - $intent: $description"
done
echo ""

# Function to create session
create_session() {
    local user_id="${1:-shell-client}"

    # Send status messages to stderr so they don't interfere with session ID capture
    echo -e "${YELLOW}Creating session for user: $user_id${NC}" >&2

    # Create empty JSON payload
    echo '{}' > /tmp/empty_session.json

    # Call session creation endpoint
    local response=$(curl -s -X POST \
        "$BASE_URL/apps/$APP_NAME/users/$user_id/sessions" \
        -H "Content-Type: application/json" \
        -d @/tmp/empty_session.json)

    # Extract session ID
    local session_id=$(echo "$response" | jq -r '.id')

    if [ "$session_id" != "null" ] && [ -n "$session_id" ]; then
        echo -e "${GREEN}✅ Session created: $session_id${NC}" >&2
        echo "" >&2
        # Only output the session ID to stdout
        echo "$session_id"
    else
        echo -e "${RED}❌ Failed to create session${NC}" >&2
        echo "$response" | jq '.' >&2 2>/dev/null || echo "$response" >&2
        echo "" >&2
        exit 1
    fi
}

# Function to build request from template
build_request() {
    local question="$1"
    local user_id="${2:-shell-client}"
    local session_id="${3:-session-$(date +%s)}"

    # Use basicQuery template from A2A spec
    cat <<EOF
{
  "appName": "$APP_NAME",
  "userId": "$user_id",
  "sessionId": "$session_id",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "$question"}]
  }
}
EOF
}

# Function to query agent using spec
query_agent() {
    local question="$1"
    local user_id="${2:-shell-client}"
    local session_id="${3:-session-$(date +%s)}"

    echo -e "${YELLOW}Question:${NC} $question"
    echo ""

    # Build request using template
    local payload=$(build_request "$question" "$user_id" "$session_id")

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

# Test 1: Check server
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

# Test 2: Run examples from agent card
echo "============================================================"
echo "Test 2: Run Examples from Agent Card"
echo "============================================================"
echo ""

# Get example names
echo "📚 Available Examples in Agent Card:"
jq -r '.agentCard.examples | keys[]' "$AGENT_CARD" | while read -r example_name; do
    echo "   - $example_name"
done
echo ""

# Create session for this test
TEST2_SESSION=$(create_session "examples-test")

# Run first example (totalCost)
echo -e "${BLUE}Running 'totalCost' example...${NC}"
echo ""

EXAMPLE_REQUEST=$(jq -r '.agentCard.examples.totalCost.request.newMessage.parts[0].text' "$AGENT_CARD")
query_agent "$EXAMPLE_REQUEST" "examples-test" "$TEST2_SESSION"

# Test 3: Test each intent with first example
echo "============================================================"
echo "Test 3: Test Intents (from Agent Card)"
echo "============================================================"
echo ""

# Create session for intent tests
TEST3_SESSION=$(create_session "intent-tests")

# Get all intents
INTENTS=$(jq -r '.agentCard.intents | keys[]' "$AGENT_CARD")

for intent in $INTENTS; do
    echo -e "${BLUE}Intent: $intent${NC}"

    # Get description
    description=$(jq -r ".agentCard.intents.\"$intent\".description" "$AGENT_CARD")
    echo "Description: $description"
    echo ""

    # Get first example
    example=$(jq -r ".agentCard.intents.\"$intent\".examples[0]" "$AGENT_CARD")

    if [ "$example" != "null" ]; then
        query_agent "$example" "intent-tests" "$TEST3_SESSION"
    fi

    echo "---"
    echo ""
done

# Test 4: Use templates from A2A spec
echo "============================================================"
echo "Test 4: Use Templates from A2A Spec"
echo "============================================================"
echo ""

# Get query templates
echo "📝 Query Templates from A2A Spec:"
jq -r '.templates.parameterizedQuery.queryTemplates | to_entries[] | "   - \(.key): \(.value)"' "$A2A_SPEC"
echo ""

# Create session for template test
TEST4_SESSION=$(create_session "template-test")

# Use totalCostByPeriod template
TEMPLATE=$(jq -r '.templates.parameterizedQuery.queryTemplates.totalCostByPeriod' "$A2A_SPEC")
QUERY=$(echo "$TEMPLATE" | sed 's/{{PERIOD}}/FY26/')

echo -e "${BLUE}Using template: totalCostByPeriod${NC}"
echo "Template: $TEMPLATE"
echo "Query: $QUERY"
echo ""

query_agent "$QUERY" "template-test" "$TEST4_SESSION"

# Test 5: Validate request schema
echo "============================================================"
echo "Test 5: Validate Request Schema"
echo "============================================================"
echo ""

echo "📋 Request Schema (required fields):"
jq -r '.agentCard.requestSchema.required[]' "$AGENT_CARD" | while read -r field; do
    echo "   - $field"
done
echo ""

# Build a test request
TEST_REQUEST=$(build_request "Test query" "validation-test")

echo "🧪 Validating test request..."
echo ""

# Note: Full JSON schema validation requires additional tools
# Here we just check required fields exist
VALID=true

for field in appName userId sessionId newMessage; do
    if echo "$TEST_REQUEST" | jq -e ".$field" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Field '$field' present${NC}"
    else
        echo -e "${RED}❌ Field '$field' missing${NC}"
        VALID=false
    fi
done

if [ "$VALID" = true ]; then
    echo ""
    echo -e "${GREEN}✅ Request is valid${NC}"
else
    echo ""
    echo -e "${RED}❌ Request validation failed${NC}"
fi

echo ""

# Test 6: Use case from A2A spec
echo "============================================================"
echo "Test 6: Run Use Case (from A2A Spec)"
echo "============================================================"
echo ""

echo "📖 Available Use Cases:"
jq -r '.useCases | keys[]' "$A2A_SPEC" | while read -r use_case; do
    echo "   - $use_case"
done
echo ""

# Run monitoring agent use case
echo -e "${BLUE}Simulating 'monitoringAgent' use case...${NC}"
echo ""

USE_CASE_QUERY=$(jq -r '.useCases.monitoringAgent.workflow[0].request.newMessage.parts[0].text' "$A2A_SPEC")
USE_CASE_USER=$(jq -r '.useCases.monitoringAgent.workflow[0].request.userId' "$A2A_SPEC")

# Create session for use case test
TEST6_SESSION=$(create_session "$USE_CASE_USER")

query_agent "$USE_CASE_QUERY" "$USE_CASE_USER" "$TEST6_SESSION"

# Summary
echo "============================================================"
echo "Test Summary"
echo "============================================================"
echo ""
echo -e "${GREEN}✅ All spec-driven tests complete!${NC}"
echo ""
echo "What we tested:"
echo "  ✅ Loaded agent capabilities from agent-card.json"
echo "  ✅ Ran examples from agent-card.json"
echo "  ✅ Tested all intents with example queries"
echo "  ✅ Used query templates from a2a-spec.json"
echo "  ✅ Validated request schema"
echo "  ✅ Executed use case from a2a-spec.json"
echo ""
echo "Next steps:"
echo "  - Review specs: cat $AGENT_CARD | jq '.agentCard.metadata'"
echo "  - Try Python client: python3 examples/api_client_spec.py"
echo "  - Integrate with your agent using templates"
echo ""
