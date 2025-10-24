"""Sub-agents for FinOps Cost Data Analyst.

This module contains all specialized sub-agents that work together in a sequential workflow.
Each sub-agent has a specific role and uses tools to accomplish its task.

Architecture:
    sql_generation_agent → sql_validation_agent → query_execution_agent → insight_synthesis_agent

Each agent's output is stored in state and passed to the next agent via output_key.
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.genai import types

from .prompts import (
    get_sql_generation_prompt,
    SQL_VALIDATION_PROMPT,
    get_query_execution_prompt,
    INSIGHT_SYNTHESIS_PROMPT,
)

# Import tools from _tools package
from ._tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
    bigquery_schema_toolset,
    bigquery_execution_toolset,
    bigquery_full_toolset,
)

logger = logging.getLogger(__name__)

# Get model from environment
MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp")


# ============================================================================
# SUB-AGENT 1: SQL GENERATION (with DYNAMIC schema discovery)
# ============================================================================

sql_generation_agent = LlmAgent(
    model=MODEL,
    name="sql_generation",
    instruction=get_sql_generation_prompt(),
    output_key="sql_query",  # Stores generated SQL in state['sql_query']
    tools=[bigquery_full_toolset],  # FULL toolset: schema discovery + AI analytics
    # Tools available:
    #   - list_dataset_ids: Lists all datasets in project (CRITICAL for discovery)
    #   - list_table_ids: Lists all tables in dataset (CRITICAL for discovery)
    #   - get_table_info: Fetches table schema dynamically from BigQuery (CRITICAL)
    #   - get_dataset_info: Fetches dataset metadata
    #   - execute_sql: Executes SQL queries (available in full toolset)
    #   - forecast: BigQuery AI time series forecasting for anomaly detection
    #   - ask_data_insights: Natural language insights using BigQuery AI
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Slightly higher to encourage tool usage for schema discovery
    ),
)

logger.info("✓ SQL Generation Agent initialized with BigQuery full toolset")


# ============================================================================
# SUB-AGENT 2: SQL VALIDATION
# ============================================================================

sql_validation_agent = LlmAgent(
    model=MODEL,
    name="sql_validation",
    instruction=SQL_VALIDATION_PROMPT,
    output_key="validation_result",  # Stores "VALID" or "INVALID: reason" in state
    tools=[
        check_forbidden_keywords,
        parse_sql_query,
        validate_sql_security,
    ],  # type: ignore
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Deterministic for security validation
    ),
)

logger.info("✓ SQL Validation Agent initialized with validation tools")


# ============================================================================
# SUB-AGENT 3: QUERY EXECUTION
# ============================================================================

query_execution_agent = LlmAgent(
    model=MODEL,
    name="query_execution",
    instruction=get_query_execution_prompt(),
    output_key="query_results",  # Stores BigQuery results in state['query_results']
    tools=[bigquery_execution_toolset],  # Dedicated execution toolset (execute_sql only)
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Deterministic for query execution
    ),
)

logger.info("✓ Query Execution Agent initialized with BigQuery execution toolset")


# ============================================================================
# SUB-AGENT 4: INSIGHT SYNTHESIS
# ============================================================================

insight_synthesis_agent = LlmAgent(
    model=MODEL,
    name="insight_synthesis",
    instruction=INSIGHT_SYNTHESIS_PROMPT,
    # NO output_key - this is the LAST agent, it returns directly to user
    # output_key would write to state, but there's no next agent to read it
    # No tools needed - just formatting
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,  # Balanced temperature for natural text generation without echoing
    ),
)

logger.info("✓ Insight Synthesis Agent initialized (formatting only)")


# Export all sub-agents
__all__ = [
    "sql_generation_agent",
    "sql_validation_agent",
    "query_execution_agent",
    "insight_synthesis_agent",
]

logger.info("✓ All sub-agents initialized successfully")
