"""BigQuery tools for query execution.

This module provides the BigQuery toolset used by the Query Execution sub-agent
to safely execute validated SQL queries against BigQuery.
"""

from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

# Create BigQueryToolset for query execution
# Configuration blocks all write operations for safety
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED,  # Block all write operations (INSERT, UPDATE, DELETE)
)

# Initialize toolset with only execute_sql enabled
bigquery_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],  # Only allow query execution (read-only)
    bigquery_tool_config=bigquery_tool_config,
)
