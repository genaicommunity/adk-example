"""BigQuery Executor Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types
from .prompts import BIGQUERY_EXECUTOR_INSTRUCTION


def get_bigquery_executor_agent() -> LlmAgent:
    """Create and return the BigQuery Executor agent with BigQuery tools."""

    # Create BigQueryToolset for query execution
    # Filter to only execute_sql tool for running validated queries
    bigquery_tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,  # Block all write operations for safety
    )
    bigquery_toolset = BigQueryToolset(
        tool_filter=["execute_sql"],
        bigquery_tool_config=bigquery_tool_config,
    )

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="bigquery_executor",
        instruction=BIGQUERY_EXECUTOR_INSTRUCTION,
        tools=[bigquery_toolset],
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
    )

    return agent
