"""SQL Validator Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import SQL_VALIDATOR_INSTRUCTION


def get_sql_validator_agent() -> LlmAgent:
    """Create and return the SQL Validator agent."""

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="sql_validator",
        instruction=SQL_VALIDATOR_INSTRUCTION,
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
    )

    return agent
