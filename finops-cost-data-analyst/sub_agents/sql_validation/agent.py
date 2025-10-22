"""SQL Validation Agent - validates SQL for security using tools.

This agent USES REAL TOOLS to validate SQL queries.
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

from prompts import SQL_VALIDATION_PROMPT
from .tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
)


# Create the agent instance with validation tools
sql_validation_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="sql_validation",
    instruction=SQL_VALIDATION_PROMPT,
    tools=[
        check_forbidden_keywords,
        parse_sql_query,
        validate_sql_security,
    ],  # type: ignore
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Deterministic for security validation
    ),
)
