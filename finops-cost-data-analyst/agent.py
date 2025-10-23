"""Root Agent - FinOps Cost Data Analyst with Sequential Multi-Agent Workflow.

This is the enterprise-grade root agent following ADK best practices.
Tools are organized in _tools/ package (underscore prefix hides from ADK discovery).

Architecture:
    Root Agent (SequentialAgent)
        ↓ orchestrates
    Sub-Agents (sql_generation, sql_validation, query_execution, insight_synthesis)
        ↓ each sub-agent's output goes to next sub-agent via state
    Real Tools (from _tools package)
"""

import logging
import os

from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

from .prompts import (
    ROOT_AGENT_DESCRIPTION,
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
    bigquery_toolset,            # Legacy execution toolset
    bigquery_schema_toolset,     # Schema discovery toolset
    bigquery_execution_toolset,  # Query execution toolset
    bigquery_full_toolset,       # Schema discovery + AI analytics toolset
)

logger = logging.getLogger(__name__)


# ============================================================================
# SUB-AGENT 1: SQL GENERATION (with DYNAMIC schema discovery)
# ============================================================================

sql_generation_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
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


# ============================================================================
# SUB-AGENT 2: SQL VALIDATION
# ============================================================================

sql_validation_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
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


# ============================================================================
# SUB-AGENT 3: QUERY EXECUTION
# ============================================================================

query_execution_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="query_execution",
    instruction=get_query_execution_prompt(),
    output_key="query_results",  # Stores BigQuery results in state['query_results']
    tools=[bigquery_execution_toolset],  # Dedicated execution toolset (execute_sql only)
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Deterministic for query execution
    ),
)


# ============================================================================
# SUB-AGENT 4: INSIGHT SYNTHESIS
# ============================================================================

insight_synthesis_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="insight_synthesis",
    instruction=INSIGHT_SYNTHESIS_PROMPT,
    output_key="final_insights",  # CRITICAL: SequentialAgent returns this to user
    # No tools needed - just formatting
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,  # Balanced temperature for natural text generation without echoing
    ),
)


# ============================================================================
# ROOT AGENT - SequentialAgent orchestrating all sub-agents
# ============================================================================

# Create root agent with sequential workflow
# Each sub-agent's output feeds into the next via shared state
# By default, SequentialAgent returns the output of the LAST agent
root_agent = SequentialAgent(
    name="FinOpsCostAnalystOrchestrator",
    description=ROOT_AGENT_DESCRIPTION,
    sub_agents=[
        sql_generation_agent,      # Outputs: state['sql_query']
        sql_validation_agent,       # Uses: state['sql_query'], Outputs: state['validation_result']
        query_execution_agent,      # Uses: state['sql_query'], Outputs: state['query_results']
        insight_synthesis_agent,    # LAST agent - its output will be shown to user
    ],
)

logger.info("✓ Root Agent (SequentialAgent) initialized with 4 sub-agents")

# Export for ADK
__all__ = ["root_agent"]
