"""BigQuery Executor Agent implementation - executes SQL on BigQuery.

This sub-agent uses ADK's BigQueryToolset to execute validated SQL queries.

Architecture:
    Root Agent → BigQuery Executor Sub-Agent → BigQueryToolset (ADK built-in)
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

# Import centralized prompts
from PROMPT_INSTRUCTION import get_bigquery_executor_instruction


def get_bigquery_executor_agent() -> LlmAgent:
    """Create and return the BigQuery Executor agent with BigQuery tools.

    Tools provided:
    - execute_sql (from ADK BigQueryToolset): Execute SQL queries on BigQuery

    Security:
    - WriteMode.BLOCKED prevents any write operations (INSERT, UPDATE, DELETE, etc.)
    - Only SELECT queries can be executed

    Returns:
        LlmAgent configured with BigQuery execution tools
    """

    # Create BigQueryToolset for query execution
    # Filter to only execute_sql tool for running validated queries
    bigquery_tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,  # Block all write operations for safety
    )
    bigquery_toolset = BigQueryToolset(
        tool_filter=["execute_sql"],  # Only allow query execution
        bigquery_tool_config=bigquery_tool_config,
    )

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="bigquery_executor",
        instruction=get_bigquery_executor_instruction(),
        tools=[bigquery_toolset],
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0,  # Deterministic for query execution
        ),
    )

    return agent
