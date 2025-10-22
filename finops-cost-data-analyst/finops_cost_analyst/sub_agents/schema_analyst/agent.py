"""Schema Analyst Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types
from .prompts import SCHEMA_ANALYST_INSTRUCTION


def get_schema_analyst_agent() -> LlmAgent:
    """Create and return the Schema Analyst agent with BigQuery tools."""

    # Create BigQueryToolset for schema analysis
    # Filter to only schema-related tools (list_tables, get_table_schema)
    bigquery_tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,  # Block all write operations for safety
    )
    bigquery_toolset = BigQueryToolset(
        tool_filter=["list_tables", "get_table_schema"],
        bigquery_tool_config=bigquery_tool_config,
    )

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="schema_analyst",
        instruction=SCHEMA_ANALYST_INSTRUCTION,
        tools=[bigquery_toolset],
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
    )

    return agent
