"""FinOps Cost Analyst Root Agent - Orchestrator.

This is the root agent that coordinates all sub-agents.

Architecture (CORRECT ENTERPRISE PATTERN for ADK):
    Root Agent → Agent Tool Wrappers → Sub-Agents → Real Tools

Where:
    - Root Agent: Has async functions as tools (agent_tools.py)
    - Agent Tool Wrappers: Thin async functions that wrap sub-agents
    - Sub-Agents: Have REAL tools attached (validation_tools, BigQueryToolset, etc.)
    - Real Tools: Actual functions that do work
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.genai import types

# Import centralized prompts
from PROMPT_INSTRUCTION import get_root_agent_instruction

# Import agent tool wrappers (these call sub-agents with real tools)
from .agent_tools import (
    call_sql_generator,
    call_sql_validator,
    call_bigquery_executor,
    call_insight_synthesizer,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_root_agent() -> LlmAgent:
    """Create and return the root FinOps Cost Analyst agent.

    This root agent orchestrates 4 specialized sub-agents through tool wrappers:
    1. call_sql_generator → sql_generator sub-agent (no tools)
    2. call_sql_validator → sql_validator sub-agent (HAS validation tools)
    3. call_bigquery_executor → bigquery_executor sub-agent (HAS BigQueryToolset)
    4. call_insight_synthesizer → insight_synthesizer sub-agent (no tools)

    Architecture:
        Root uses async functions as tools
        Those functions create sub-agents with real tools
        Sub-agents do the actual work

    Returns:
        LlmAgent configured as root orchestrator
    """

    # Agent tool wrappers - these call sub-agents (which have real tools)
    tools = [
        call_sql_generator,        # → sub-agent with no tools (schema hardcoded)
        call_sql_validator,        # → sub-agent with validation tools
        call_bigquery_executor,    # → sub-agent with BigQueryToolset
        call_insight_synthesizer,  # → sub-agent with no tools
    ]

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="finops_cost_analyst_root",
        instruction=get_root_agent_instruction(),
        tools=tools,  # type: ignore
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,  # Lower for consistent workflow execution
            top_p=0.95,
        ),
    )

    logger.info("Root agent initialized with 4 sub-agent wrappers")
    return agent


# Create the root agent instance
root_agent = get_root_agent()
