#!/bin/bash

# Interactive testing script for agents
# This script helps you test each agent with predefined queries

echo "============================================================"
echo "GOOGLE ADK AGENT INTERACTIVE TESTING"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate environment
source .venv/bin/activate

echo -e "${BLUE}Select which agent to test:${NC}"
echo "1. Time/Weather Agent (sub-agent)"
echo "2. Calculator Agent (sub-agent)"
echo "3. Main Coordinator Agent (with delegation)"
echo "4. Run all test queries"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Testing Time/Weather Agent${NC}"
        echo "============================================================"
        echo ""
        echo "Test Query 1: What time is it in Tokyo?"
        echo "Test Query 2: What's the weather in London?"
        echo "Test Query 3: Is it sunny in Paris?"
        echo ""
        read -p "Press Enter to start adk web for time_weather_agent..."
        adk web sub_agents/time_weather_agent
        ;;
    2)
        echo ""
        echo -e "${GREEN}Testing Calculator Agent${NC}"
        echo "============================================================"
        echo ""
        echo "Test Query 1: Calculate 25 times 4"
        echo "Test Query 2: What is 100 divided by 5?"
        echo "Test Query 3: Add 123 and 456"
        echo ""
        read -p "Press Enter to start adk web for calculator_agent..."
        adk web sub_agents/calculator_agent
        ;;
    3)
        echo ""
        echo -e "${GREEN}Testing Main Coordinator Agent${NC}"
        echo "============================================================"
        echo ""
        echo "Test Query 1: What time is it in Tokyo?"
        echo "Test Query 2: Calculate 15 times 8"
        echo "Test Query 3: What's the weather in London and what time is it there?"
        echo "Test Query 4: Add 50 and 75, then tell me the weather in Paris"
        echo ""
        read -p "Press Enter to start adk web for main_agent..."
        adk web main_agent
        ;;
    4)
        echo ""
        echo -e "${GREEN}Running All Test Queries (CLI)${NC}"
        echo "============================================================"
        echo ""

        echo -e "${YELLOW}Testing Time/Weather Agent:${NC}"
        echo "Query: What time is it in Tokyo?"
        echo "Starting agent..."
        echo "What time is it in Tokyo?" | adk run sub_agents/time_weather_agent

        echo ""
        echo -e "${YELLOW}Testing Calculator Agent:${NC}"
        echo "Query: Calculate 25 times 4"
        echo "Starting agent..."
        echo "Calculate 25 times 4" | adk run sub_agents/calculator_agent

        echo ""
        echo -e "${YELLOW}Testing Main Coordinator:${NC}"
        echo "Query: What's the weather in London and what time is it there?"
        echo "Starting agent..."
        echo "What's the weather in London and what time is it there?" | adk run main_agent

        echo ""
        echo -e "${GREEN}All tests completed!${NC}"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Testing complete!${NC}"
