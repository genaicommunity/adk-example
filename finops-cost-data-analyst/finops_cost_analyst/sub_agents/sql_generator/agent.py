"""SQL Generator Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import SQL_GENERATOR_INSTRUCTION


def get_sql_generator_agent() -> LlmAgent:
    """Create and return the SQL Generator agent."""

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="sql_generator",
        instruction=SQL_GENERATOR_INSTRUCTION,
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
    )

    return agent
