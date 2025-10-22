"""Query Execution Agent - executes SQL on BigQuery using ADK tools.

This agent USES ADK's BigQueryToolset to execute validated SQL queries.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

from prompts import get_query_execution_prompt


# Create BigQueryToolset for query execution
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED,  # Block all write operations for safety
)
bigquery_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],  # Only allow query execution
    bigquery_tool_config=bigquery_tool_config,
)

# Create the agent instance with BigQuery tools
query_execution_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="query_execution",
    instruction=get_query_execution_prompt(),
    tools=[bigquery_toolset],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Deterministic for query execution
    ),
)
