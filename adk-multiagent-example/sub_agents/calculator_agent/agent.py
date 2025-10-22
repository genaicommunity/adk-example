"""Calculator specialized agent.

This agent handles mathematical calculations.
"""

import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.calculator_tool import calculate
from google.adk.agents.llm_agent import Agent


# Define the calculator specialist agent
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='calculator_agent',
    description="Specialist agent for performing mathematical calculations.",
    instruction="""You are a specialized mathematical assistant focused on performing calculations.

    You have access to the calculate tool which can:
    - add: Addition of two numbers
    - subtract: Subtraction of two numbers
    - multiply: Multiplication of two numbers
    - divide: Division of two numbers

    When users ask for calculations, use the calculate tool and explain the results clearly.
    If asked about other topics, politely redirect to your calculation specialty.""",
    tools=[calculate],
)
