# Agent Evaluation Queries

Use these queries to evaluate and test each agent's capabilities.

## Time/Weather Agent Evaluation

### Basic Queries
```
What time is it in Tokyo?
What's the weather in London?
Is it raining in Seattle?
Tell me the current time in Paris.
How's the weather in Sydney?
```

### Expected Behavior
- ✅ Should use `get_current_time` for time queries
- ✅ Should use `get_weather` for weather queries
- ✅ Should respond with city name and requested information
- ❌ Should NOT handle calculation queries

### Edge Cases
```
What time is it in New York and London? (multiple cities)
What's the weather? (no city specified)
Calculate the time difference (should fail - no calculation tools)
```

---

## Calculator Agent Evaluation

### Basic Queries
```
Calculate 25 times 4
What is 100 divided by 5?
Add 123 and 456
Subtract 50 from 200
15 multiply by 8
```

### Expected Behavior
- ✅ Should use `calculate` tool for all math operations
- ✅ Should handle: add, subtract, multiply, divide
- ✅ Should handle division by zero gracefully
- ❌ Should NOT handle time/weather queries

### Edge Cases
```
What is 10 divided by 0? (division by zero)
Calculate the square root of 16 (unsupported operation)
What time is it? (should fail - no time tools)
Add 5 and 3 and multiply by 2 (multi-step - may or may not work)
```

---

## Main Coordinator Agent Evaluation

### Single Domain Queries
```
What time is it in Tokyo? (should delegate to time_weather_agent)
Calculate 15 times 8 (should delegate to calculator_agent)
What's the weather in London? (should delegate to time_weather_agent)
```

### Multi-Domain Queries (Coordination)
```
What's the weather in London and what time is it there?
Calculate 50 plus 25, then tell me the time in Paris
What time is it in Tokyo and what is 10 times 5?
Add 100 and 200, and also tell me the weather in New York
```

### Expected Behavior
- ✅ Should identify query type (time/weather vs calculation)
- ✅ Should delegate to appropriate sub-agent
- ✅ Should handle mixed queries by calling multiple sub-agents
- ✅ Should synthesize responses from multiple agents
- ✅ Should explain which specialist it's consulting

### Delegation Verification
The coordinator should:
1. Analyze the user query
2. Decide which sub-agent(s) to use
3. Delegate to sub-agent(s)
4. Return coordinated response

**Look for phrases like:**
- "Let me consult the time/weather specialist..."
- "I'll ask the calculator agent..."
- "Delegating to..."

---

## Evaluation Criteria

### 1. Tool Usage
- [ ] Correct tool selected for query type
- [ ] Tool called with correct parameters
- [ ] Tool response properly formatted

### 2. Delegation (Main Agent Only)
- [ ] Correctly identifies which sub-agent to use
- [ ] Successfully delegates to sub-agent
- [ ] Handles responses from multiple sub-agents
- [ ] Explains delegation process to user

### 3. Error Handling
- [ ] Handles invalid inputs gracefully
- [ ] Provides helpful error messages
- [ ] Doesn't crash on edge cases

### 4. Response Quality
- [ ] Clear and concise responses
- [ ] Includes all requested information
- [ ] Natural language (conversational)

---

## Testing Checklist

### Tools (Unit Tests)
```bash
python tests/test_tools.py
```
- [ ] `get_current_time` works
- [ ] `get_weather` works
- [ ] `calculate` works (all operations)
- [ ] Error cases handled

### Sub-Agents (Integration Tests)
```bash
# Test time/weather agent
adk run sub_agents/time_weather_agent
# Try queries from "Time/Weather Agent Evaluation" section

# Test calculator agent
adk run sub_agents/calculator_agent
# Try queries from "Calculator Agent Evaluation" section
```

### Main Coordinator (E2E Tests)
```bash
adk run main_agent
# Try queries from "Main Coordinator Agent Evaluation" section
```

### Delegation Verification
- [ ] Main agent does NOT directly use tools
- [ ] Main agent delegates to sub-agents
- [ ] Sub-agents use tools
- [ ] Responses flow: Main → Sub → Tool → Sub → Main → User

---

## Performance Metrics

Track these for evaluation:

### Response Time
- Time from query to response
- Acceptable: < 5 seconds for simple queries
- Acceptable: < 10 seconds for multi-agent queries

### Accuracy
- Does it answer the question correctly?
- Does it use the right tools/agents?
- Are calculations correct?

### Delegation Success Rate
- % of queries correctly routed to right sub-agent
- % of multi-domain queries handled correctly

---

## Automated Testing

### Quick Test All
```bash
./tests/test_agents_interactive.sh
```

### Individual Tests
```bash
# Test tools only
python tests/test_tools.py

# Test specific agent
adk run sub_agents/time_weather_agent
adk run sub_agents/calculator_agent
adk run main_agent
```

---

## Debugging Tips

### Agent Not Responding
1. Check API key in `.env`
2. Verify model name is correct
3. Check network connection

### Wrong Tool Used
1. Review agent instructions
2. Check tool descriptions
3. Verify tool is in agent's tools list

### Delegation Not Working
1. Verify main agent has `sub_agents`, not `tools`
2. Check sub-agent loading in main_agent/agent.py
3. Review delegation instructions

### Tool Errors
1. Run `python tests/test_tools.py`
2. Check tool function signatures
3. Verify imports in tools/__init__.py
