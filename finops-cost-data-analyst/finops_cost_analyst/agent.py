"""FinOps Cost Analyst Root Agent."""

import logging
import os

from google.adk.agents import LlmAgent
from google.genai import types

from .prompts import return_instructions_root
from .tools import (
    call_bigquery_executor,
    call_insight_synthesizer,
    call_sql_generator,
    call_sql_validator,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_root_agent() -> LlmAgent:
    """Create and return the root FinOps Cost Analyst agent."""

    # Tools to call sub-agents
    # Schema is now hardcoded in SQL generator for performance (eliminates 2+ min BigQuery fetch)
    tools = [
        call_sql_generator,
        call_sql_validator,
        call_bigquery_executor,
        call_insight_synthesizer,
    ]

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="finops_cost_analyst_root",
        instruction=return_instructions_root(),
        tools=tools,  # type: ignore
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,  # Lower for consistent workflow execution
            top_p=0.95,
        ),
    )

    return agent


# Create the root agent instance
root_agent = get_root_agent()
