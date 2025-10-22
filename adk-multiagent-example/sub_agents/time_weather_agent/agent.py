"""Time and Weather specialized agent.

This agent handles time and weather-related queries.
"""

import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.time_tool import get_current_time
from tools.weather_tool import get_weather
from google.adk.agents.llm_agent import Agent


# Define the time and weather specialist agent
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='time_weather_agent',
    description="Specialist agent for time and weather information across different cities.",
    instruction="""You are a specialized assistant focused on providing time and weather information.

    You have access to two tools:
    - get_current_time: Get the current time for any city
    - get_weather: Get weather information for any city

    When users ask about time or weather, use the appropriate tool and provide clear,
    friendly responses. If asked about other topics, politely redirect to your specialty areas.""",
    tools=[get_current_time, get_weather],
)
