"""BigQuery tools for dynamic schema discovery and query execution.

This module provides the comprehensive BigQuery toolset used by agents for:
- Dynamic schema discovery (get_table_info, get_dataset_info)
- Metadata exploration (list_dataset_ids, list_table_ids)
- Query execution (execute_sql)
- Advanced analytics (forecast, ask_data_insights)

All write operations are BLOCKED for security.
"""

from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

# =============================================================================
# BIGQUERY TOOLSET CONFIGURATION
# =============================================================================

# Create BigQueryToolset with comprehensive capabilities
# Configuration blocks all write operations for security
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED,  # Block all write operations (INSERT, UPDATE, DELETE)
)

# =============================================================================
# SCHEMA DISCOVERY TOOLSET (for SQL Generation Agent)
# =============================================================================

# Toolset for SQL Generation Agent - enables dynamic schema discovery & table selection
bigquery_schema_toolset = BigQueryToolset(
    tool_filter=[
        "get_table_info",      # Get table metadata including schema (CRITICAL for dynamic discovery)
        "get_dataset_info",    # Get dataset metadata
        "list_table_ids",      # List all tables in dataset (for exploration)
        "list_dataset_ids",    # List all datasets in project (CRITICAL for multi-table discovery)
    ],
    bigquery_tool_config=bigquery_tool_config,
)

# =============================================================================
# QUERY EXECUTION TOOLSET (for Query Execution Agent)
# =============================================================================

# Toolset for Query Execution Agent - only SQL execution
bigquery_execution_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],  # Only allow query execution (read-only)
    bigquery_tool_config=bigquery_tool_config,
)

# =============================================================================
# ADVANCED ANALYTICS TOOLSET (Optional - for future expansion)
# =============================================================================

# Toolset for advanced analytics capabilities
bigquery_analytics_toolset = BigQueryToolset(
    tool_filter=[
        "execute_sql",         # SQL execution
        "forecast",            # BigQuery AI time series forecasting
        "ask_data_insights",   # Natural language data insights
    ],
    bigquery_tool_config=bigquery_tool_config,
)

# =============================================================================
# COMBINED TOOLSET (Schema Discovery + AI Analytics)
# =============================================================================

# Toolset combining schema discovery with AI analytics for advanced SQL Generation
# This gives the SQL Generation Agent full capabilities:
# - Multi-table discovery (list_dataset_ids, list_table_ids)
# - Schema fetching (get_table_info, get_dataset_info)
# - ML-based forecasting (forecast)
# - Natural language insights (ask_data_insights)
bigquery_full_toolset = BigQueryToolset(
    tool_filter=[
        # Schema Discovery Tools
        "get_table_info",      # Get table metadata including schema
        "get_dataset_info",    # Get dataset metadata
        "list_table_ids",      # List all tables in dataset
        "list_dataset_ids",    # List all datasets in project
        # AI Analytics Tools
        "forecast",            # BigQuery AI time series forecasting
        "ask_data_insights",   # Natural language data insights
    ],
    bigquery_tool_config=bigquery_tool_config,
)

# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# Alias for backward compatibility (used by existing Query Execution Agent)
bigquery_toolset = bigquery_execution_toolset
