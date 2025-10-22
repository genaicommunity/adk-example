"""SQL Generator Agent implementation - converts natural language to SQL.

This sub-agent generates BigQuery SQL from user questions.
Schema is hardcoded in the prompt for performance (no tool calls needed).

Architecture:
    Root Agent → SQL Generator Sub-Agent (no tools needed)
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

# Import centralized prompts
from PROMPT_INSTRUCTION import get_sql_generator_instruction


def get_sql_generator_agent() -> LlmAgent:
    """Create and return the SQL Generator agent.

    This agent does NOT use tools - schema is hardcoded in the instruction
    for performance (eliminates 2+ minute BigQuery schema fetch).

    Business logic enforced:
    - GenAI queries → managed_service = 'AI/ML'
    - FY26 → dates between 2025-02-01 and 2026-01-31
    - FY25 → dates between 2024-02-01 and 2025-01-31

    Returns:
        LlmAgent configured for SQL generation
    """

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="sql_generator",
        instruction=get_sql_generator_instruction(),
        # No tools needed - schema hardcoded for performance
        generate_content_config=types.GenerateContentConfig(
            temperature=0.01,  # Very low for deterministic SQL generation
        ),
    )

    return agent
