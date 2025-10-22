"""Tools package - actual functions that perform work.

These are the real tools used by sub-agents:

BigQuery Tools:
    - execute_bigquery_query: Execute SQL on BigQuery
    - describe_bigquery_table: Get table schema (not currently used)

Validation Tools:
    - check_forbidden_keywords: Check for SQL injection attempts
    - parse_sql_query: Validate SQL syntax
    - validate_sql_security: Complete validation (combines both)

Architecture:
    Root Agent → Sub-Agents → These Tools

"""

from .bigquery_tools import (
    execute_bigquery_query,
    describe_bigquery_table,
)

from .validation_tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
)

__all__ = [
    "execute_bigquery_query",
    "describe_bigquery_table",
    "check_forbidden_keywords",
    "parse_sql_query",
    "validate_sql_security",
]
