"""Tools package for FinOps Cost Data Analyst.

This package contains all tools used by sub-agents:
- validation_tools: SQL validation and security checking
- bigquery_tools: BigQuery toolsets for schema discovery, query execution, and analytics
"""

from .validation_tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
)
from .bigquery_tools import (
    bigquery_toolset,            # Backward compatibility (execution only)
    bigquery_schema_toolset,     # Schema discovery for SQL Generation Agent
    bigquery_execution_toolset,  # Query execution for Query Execution Agent
    bigquery_analytics_toolset,  # Advanced analytics (forecast, insights)
)

__all__ = [
    # Validation tools
    "check_forbidden_keywords",
    "parse_sql_query",
    "validate_sql_security",
    # BigQuery toolsets
    "bigquery_toolset",           # Legacy/default
    "bigquery_schema_toolset",    # Schema discovery
    "bigquery_execution_toolset", # Query execution
    "bigquery_analytics_toolset", # Advanced analytics
]
