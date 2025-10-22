"""SQL Validator Agent implementation - validates SQL for security.

This sub-agent uses validation tools to check SQL queries.

Architecture:
    Root Agent → SQL Validator Sub-Agent → Validation Tools
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

# Import centralized prompts
from PROMPT_INSTRUCTION import get_sql_validator_instruction

# Import validation tools
from tools.validation_tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
)


def get_sql_validator_agent() -> LlmAgent:
    """Create and return the SQL Validator agent with validation tools.

    Tools provided:
    - check_forbidden_keywords: Check for SQL injection attempts
    - parse_sql_query: Validate SQL syntax
    - validate_sql_security: Complete validation (convenience function)

    Returns:
        LlmAgent configured with validation tools
    """

    # Tools for SQL validation
    tools = [
        check_forbidden_keywords,
        parse_sql_query,
        validate_sql_security,
    ]

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="sql_validator",
        instruction=get_sql_validator_instruction(),
        tools=tools,  # type: ignore
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0,  # Deterministic for security validation
        ),
    )

    return agent
