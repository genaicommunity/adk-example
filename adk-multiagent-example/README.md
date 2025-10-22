# Google ADK Multi-Agent System

A production-ready multi-agent system using Google's Agent Development Kit (ADK), demonstrating hierarchical agent delegation and modular tool architecture.

## Overview

This project implements a **multi-agent delegation architecture** where:
- **Main Coordinator Agent**: Delegates tasks to specialized sub-agents
- **Sub-Agents**: Domain experts with specific tools (time/weather, calculator)
- **Tools Library**: Reusable, modular tools shared across agents

**Key Design:** The main agent has NO tools - it only coordinates and delegates to specialists!

## Quick Start

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run tests
python eval/test_tools.py
pytest eval/test_eval.py -v

# 3. Run the agent
adk run main_agent

# 4. Try queries like:
# "What time is it in Tokyo?"
# "Calculate 15 times 8"
# "What's the weather in London and what time is it there?"
```

For detailed guide, see **[GUIDE.md](GUIDE.md)** | For testing, see **[eval/README.md](eval/README.md)**

## Project Structure

```
adk-multiagent-example/
├── main_agent/                    # Coordinator
│   ├── agent.py                   # Delegates to sub-agents (NO tools)
│   └── .env                       # Configuration
├── sub_agents/                    # Specialists
│   ├── time_weather_agent/        # Time & weather expert
│   │   └── agent.py               # Has time/weather tools
│   └── calculator_agent/          # Math expert
│       └── agent.py               # Has calculator tool
├── tools/                         # Shared library
│   ├── time_tool.py
│   ├── weather_tool.py
│   └── calculator_tool.py
├── eval/                          # Testing & evaluation
│   ├── test_eval.py               # ADK-style agent evaluation
│   ├── test_tools.py              # Unit tests
│   ├── eval_data/                 # Test datasets
│   └── README.md                  # Testing guide
├── README.md                      # This file
├── GUIDE.md                       # Detailed guide
└── requirements.txt
```

## Architecture

### How It Works

```
User Query: "What time is it in Tokyo?"
    ↓
Main Coordinator Agent
    ↓ (analyzes query)
    ↓ (decides: time query → time_weather_agent)
    ↓
Time/Weather Agent
    ↓ (uses get_current_time tool)
    ↓
Response: "The current time in Tokyo is 2:30 PM"
```

### Why This Architecture?

1. **Clear Separation** - Each agent has one responsibility
2. **Scalable** - Add new specialists without changing existing code
3. **Reusable** - Tools shared across multiple agents
4. **Maintainable** - Easy to test and update individual components

## Setup

### Prerequisites
- Python 3.9+
- Google API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
# Edit .env and main_agent/.env
GOOGLE_API_KEY=your-api-key-here
```

## Usage

### Run Main Coordinator
```bash
adk run main_agent
```

### Run Web Interface
```bash
adk web main_agent
```

### Run Individual Specialists (for testing)
```bash
adk run sub_agents/time_weather_agent
adk run sub_agents/calculator_agent
```

## Capabilities

### Main Coordinator
- Handles any query type
- Intelligently delegates to specialists
- Combines responses from multiple agents

### Time/Weather Agent
- Get current time for any city
- Get weather information

### Calculator Agent
- Addition, subtraction
- Multiplication, division

## Testing

Comprehensive testing following Google ADK patterns:

```bash
# Unit tests
python eval/test_tools.py

# Agent evaluation (ADK pattern)
pytest eval/test_eval.py -v

# Interactive testing
./eval/test_agents_interactive.sh
```

**See [eval/README.md](eval/README.md) for complete testing guide.**

**Test Coverage:**
- ✅ All tools unit tested
- ✅ Agent delegation validation
- ✅ Multi-domain query handling
- ✅ Edge cases (division by zero, etc.)
- ✅ 10 evaluation test cases

## Extending the System

### Add a New Tool

1. Create in `tools/`:
```python
# tools/search_tool.py
def web_search(query: str) -> dict:
    """Search the web."""
    return {"results": "..."}
```

2. Export in `tools/__init__.py`:
```python
from .search_tool import web_search
__all__ = [..., 'web_search']
```

3. Add to an agent:
```python
from tools import web_search
root_agent = Agent(tools=[web_search], ...)
```

### Add a New Sub-Agent

```bash
# 1. Create directory
mkdir -p sub_agents/research_agent

# 2. Create agent.py following sub_agents/calculator_agent/agent.py pattern

# 3. Update main_agent/agent.py to include it in sub_agents list
```

See **[GUIDE.md](GUIDE.md)** for detailed examples.

## Key Files Explained

| File | Purpose |
|------|---------|
| `main_agent/agent.py` | Coordinator - delegates to sub-agents |
| `sub_agents/*/agent.py` | Specialists - have specific tools |
| `tools/*.py` | Reusable tool implementations |
| `tools/__init__.py` | Tool exports for easy importing |
| `eval/test_eval.py` | ADK-style agent evaluation tests |
| `eval/test_tools.py` | Unit tests for tools |
| `eval/eval_data/` | Test datasets with input/output expectations |

## Important Design Principles

### ✅ DO
- Keep main agent as coordinator only (no tools)
- Give each sub-agent specific, focused tools
- Share tools through the tools/ library
- Use clear agent descriptions for delegation
- Test sub-agents independently

### ❌ DON'T
- Give main agent direct tool access (defeats delegation)
- Duplicate tools across agents
- Embed tool logic in agent files
- Create overly complex sub-agents

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Warning: No agents found` | **Run from project root**, not from `main_agent/` directory |
| `Failed to load agents` | Ensure you're in the project root: `cd /path/to/google-adk-agents` |
| `ModuleNotFoundError: tools` | Check sys.path.append() in agent.py |
| `ModuleNotFoundError: google.adk` | Run `pip install -r requirements.txt` |
| Authentication errors | Verify GOOGLE_API_KEY in .env files |
| Agent not delegating | Ensure main agent uses `sub_agents`, not `tools` |

## Resources

- **[GUIDE.md](GUIDE.md)** - Complete usage guide
- [Google ADK Docs](https://google.github.io/adk-docs/)
- [Multi-Agent Guide](https://google.github.io/adk-docs/agents/multi-agents/)
- [Python API Reference](https://google.github.io/adk-docs/reference/python/)

## License

Educational sample project demonstrating Google ADK multi-agent architecture.
