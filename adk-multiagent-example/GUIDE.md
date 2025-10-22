# Google ADK Multi-Agent Guide

## Quick Start

**IMPORTANT:** Always run commands from the project root directory (`google-adk-agents/`), NOT from inside `main_agent/`

### 1. Navigate to Project Root
```bash
cd /path/to/google-adk-agents  # Ensure you're in the project root
pwd  # Should show: .../google-adk-agents
```

### 2. Activate Environment
```bash
source .venv/bin/activate
```

Your API key is already configured in `.env` and `main_agent/.env`

### 3. Run the Agent
```bash
# From project root:
adk run main_agent
```

Or use the web interface:
```bash
# From project root:
adk web main_agent
```

### 3. Try These Queries
- "What time is it in Tokyo?"
- "What's the weather in London?"
- "Calculate 25 times 4"
- "What time is it in Paris and what's the weather there?"

---

## How It Works

### Multi-Agent Delegation Architecture

```
┌─────────────────────────────────────┐
│   Main Coordinator Agent            │
│   • Receives user query             │
│   • Decides which specialist to use │
│   • Delegates to sub-agents         │
└──────────┬──────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────┐
│ Time/   │  │Calculator│
│ Weather │  │ Agent   │
│ Agent   │  │         │
│ • time  │  │ • math  │
│ • weather│ │         │
└─────────┘  └─────────┘
```

**Key Point:** Main agent has NO tools - it only delegates to specialists!

---

## Project Structure

```
google-adk-agents/
├── main_agent/
│   ├── agent.py          # Coordinator (delegates to sub-agents)
│   └── .env
├── sub_agents/
│   ├── time_weather_agent/
│   │   └── agent.py      # Has time & weather tools
│   └── calculator_agent/
│       └── agent.py      # Has calculator tool
└── tools/                # Shared tools library
    ├── time_tool.py
    ├── weather_tool.py
    └── calculator_tool.py
```

---

## Adding New Features

### Add a New Tool

1. **Create the tool** in `tools/`:
```python
# tools/search_tool.py
def web_search(query: str) -> dict:
    """Search the web for information."""
    # Implementation
    return {"results": "..."}
```

2. **Export it** in `tools/__init__.py`:
```python
from .search_tool import web_search
__all__ = [..., 'web_search']
```

3. **Add to a sub-agent** (or create new one):
```python
# sub_agents/research_agent/agent.py
from tools import web_search

root_agent = Agent(
    tools=[web_search],
    # ...
)
```

### Add a New Sub-Agent

1. **Create directory**:
```bash
mkdir -p sub_agents/research_agent
```

2. **Create agent file**:
```python
# sub_agents/research_agent/__init__.py
"""Research agent package."""
__version__ = "0.1.0"

# sub_agents/research_agent/agent.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools import web_search
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='research_agent',
    description="Specialist in web research and information gathering.",
    instruction="You are a research specialist...",
    tools=[web_search],
)
```

3. **Register in main agent**:
```python
# main_agent/agent.py
research_agent = load_agent_from_path(
    Path(__file__).parent.parent / "sub_agents/research_agent/agent.py"
)

root_agent = Agent(
    sub_agents=[..., research_agent],
)
```

---

## Run Individual Agents

You can run any sub-agent independently for testing:

```bash
# Time & Weather specialist
adk run sub_agents/time_weather_agent

# Calculator specialist
adk run sub_agents/calculator_agent
```

---

## Architecture Benefits

### Why Multi-Agent?

1. **Separation of Concerns**
   - Each agent is an expert in its domain
   - Easy to understand and maintain

2. **Scalability**
   - Add new specialists without changing existing code
   - Each agent can use different models/configs

3. **Reusability**
   - Tools are shared across agents
   - No code duplication

4. **Flexibility**
   - Run agents independently for testing
   - Or coordinate them through main agent

---

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'tools'`
**Solution:** The `sys.path.append()` in each agent.py handles this. Check the path is correct.

**Issue:** `ModuleNotFoundError: No module named 'google.adk'`
**Solution:** Run `pip install -r requirements.txt` in activated venv

**Issue:** Authentication errors
**Solution:** Check `.env` and `main_agent/.env` have valid `GOOGLE_API_KEY`

**Issue:** Agent not delegating
**Solution:** Main agent needs `sub_agents` parameter, not `tools`

---

## Best Practices

1. ✅ **Keep tools pure** - Stateless functions, one responsibility
2. ✅ **Clear agent descriptions** - Help main agent delegate correctly
3. ✅ **Document everything** - Docstrings with Args and Returns
4. ✅ **Test independently** - Run each sub-agent standalone first
5. ✅ **Share tools** - Use tools/ library, avoid duplication

---

## Example: Adding a Database Agent

```bash
# 1. Create the agent
mkdir -p sub_agents/database_agent

# 2. Create tool
cat > tools/database_tool.py << 'EOF'
def query_database(sql: str) -> dict:
    """Execute SQL query and return results."""
    # Implementation
    return {"data": [...]}
EOF

# 3. Create agent
cat > sub_agents/database_agent/agent.py << 'EOF'
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools import query_database
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='database_agent',
    description="Specialist in database queries and data retrieval.",
    instruction="You are a database expert...",
    tools=[query_database],
)
EOF

# 4. Update main agent to include new sub-agent
# Add to main_agent/agent.py
```

---

## Testing & Evaluation

### Quick Test - Run All Tools
```bash
python tests/test_tools.py
```

This runs unit tests for all tools and validates:
- ✅ Time tool works correctly
- ✅ Weather tool works correctly
- ✅ Calculator tool handles all operations
- ✅ Error cases are handled properly

### Test Individual Agents

#### 1. Test Sub-Agents Independently
```bash
# Test time/weather specialist
adk run sub_agents/time_weather_agent

# Test calculator specialist
adk run sub_agents/calculator_agent
```

**Try these queries:**
- Time/Weather: "What time is it in Tokyo?", "What's the weather in London?"
- Calculator: "Calculate 25 times 4", "What is 100 divided by 5?"

#### 2. Test Main Coordinator
```bash
adk run main_agent
```

**Try these queries:**
- Single domain: "What time is it in Paris?"
- Single domain: "Calculate 15 times 8"
- Multi-domain: "What's the weather in London and what time is it there?"
- Multi-domain: "Add 50 and 75, then tell me the weather in Tokyo"

### Interactive Testing
```bash
./tests/test_agents_interactive.sh
```

This script provides:
- Menu-driven agent selection
- Pre-defined test queries
- Web interface launch

### Evaluation Checklist

For complete evaluation queries and criteria, see **[tests/evaluation_queries.md](tests/evaluation_queries.md)**

#### Tools (Unit Level)
- [ ] All tools import successfully
- [ ] Each tool returns correct data structure
- [ ] Error handling works (division by zero, invalid operations)

#### Sub-Agents (Integration Level)
- [ ] Agent loads without errors
- [ ] Correct tools are available
- [ ] Agent uses appropriate tool for query
- [ ] Responses are clear and accurate

#### Main Coordinator (E2E Level)
- [ ] Identifies query type correctly
- [ ] Delegates to appropriate sub-agent
- [ ] Handles multi-domain queries
- [ ] Synthesizes responses from multiple agents
- [ ] Explains which specialist it's consulting

### Delegation Verification

**Key Test:** Main agent should NOT use tools directly

```bash
# Verify main agent structure
grep -A 1 "sub_agents=" main_agent/agent.py
# Should show: sub_agents=[time_weather_agent, calculator_agent]

grep "tools=" main_agent/agent.py
# Should NOT have a tools parameter
```

### Performance Testing

Track these metrics:

| Metric | Target | Test Query |
|--------|--------|------------|
| Response time (simple) | < 5s | "What time is it in Tokyo?" |
| Response time (complex) | < 10s | "Weather in London and time there?" |
| Delegation accuracy | 100% | All test queries route correctly |
| Tool accuracy | 100% | Calculator gives correct results |

### Test Queries by Category

#### Time Queries
```
What time is it in Tokyo?
Tell me the current time in Paris
What's the time in London and New York?
```

#### Weather Queries
```
What's the weather in London?
Is it sunny in Paris?
How's the weather in Tokyo?
```

#### Calculator Queries
```
Calculate 25 times 4
What is 100 divided by 5?
Add 123 and 456
Subtract 50 from 200
```

#### Multi-Domain Queries (Coordinator Only)
```
What's the weather in London and what time is it there?
Calculate 50 plus 25, then tell me the time in Paris
What time is it in Tokyo and what is 10 times 5?
```

### Debugging Failed Tests

**Agent doesn't delegate:**
- Check: Main agent has `sub_agents`, not `tools`
- Check: Sub-agent descriptions are clear
- Check: Instructions mention delegation

**Tool not working:**
```bash
python tests/test_tools.py  # Run unit tests
```

**Agent not found:**
- Ensure you're in project root
- Check agent.py has `root_agent` defined

**No response:**
- Verify API key in `.env`
- Check network connection
- Try simpler query first

---

## Resources

- **[tests/evaluation_queries.md](tests/evaluation_queries.md)** - Complete evaluation guide
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Multi-Agent Systems Guide](https://google.github.io/adk-docs/agents/multi-agents/)
- [Python API Reference](https://google.github.io/adk-docs/reference/python/)

---

## Summary

This project uses **Multi-Agent Delegation**:
- Main agent = Coordinator (no tools)
- Sub-agents = Specialists (have tools)
- Tools = Shared library (reusable)

**Testing:** Use `tests/` directory for comprehensive evaluation
- Unit tests: `python tests/test_tools.py`
- Integration: `adk run sub_agents/[agent_name]`
- E2E: `adk run main_agent`

Simple, scalable, and follows Google ADK best practices!
