"""Main parent agent that coordinates sub-agents.

This agent uses TRUE MULTI-AGENT DELEGATION:
- Delegates to specialized sub-agents instead of using tools directly
- Each sub-agent is an expert in their domain
- This demonstrates agent-to-agent collaboration

Pattern: Hierarchical Multi-Agent System
"""

import sys
from pathlib import Path

# Add parent directory to path to import sub-agents
sys.path.append(str(Path(__file__).parent.parent))

from google.adk.agents.llm_agent import Agent

# Import sub-agent definitions
# Note: In ADK, we import the agent module and use its root_agent
import importlib.util

def load_agent_from_path(agent_path):
    """Load an agent module from a file path."""
    spec = importlib.util.spec_from_file_location("agent_module", agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.root_agent


# Load sub-agents
time_weather_agent = load_agent_from_path(
    Path(__file__).parent.parent / "sub_agents/time_weather_agent/agent.py"
)

calculator_agent = load_agent_from_path(
    Path(__file__).parent.parent / "sub_agents/calculator_agent/agent.py"
)


# Define the main coordinating agent that DELEGATES to sub-agents
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='main_coordinator_agent',
    description="Main coordinator that delegates tasks to specialized sub-agents.",
    instruction="""You are an intelligent coordinator that manages specialized sub-agents.

    You have access to these sub-agents:
    - time_weather_agent: Expert in time and weather information for any city
    - calculator_agent: Expert in mathematical calculations

    Your role is to:
    1. Understand user requests clearly
    2. Determine which sub-agent is best suited for the task
    3. Delegate to the appropriate sub-agent using their expertise
    4. Synthesize responses from multiple sub-agents if needed

    When users ask about:
    - Time or weather → delegate to time_weather_agent
    - Calculations or math → delegate to calculator_agent
    - Mixed queries → coordinate between both agents

    Always explain which specialist you're consulting and why.""",
    sub_agents=[time_weather_agent, calculator_agent],
)
