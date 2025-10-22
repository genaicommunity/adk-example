"""SQL validation tools for security and syntax checking.

These tools are used by the SQL Validation sub-agent to ensure
queries are safe and well-formed before execution.
"""

import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)

# Forbidden SQL keywords that could indicate SQL injection or destructive operations
FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE",
    "CREATE", "ALTER", "GRANT", "REVOKE", "MERGE",
    "EXEC", "EXECUTE", "CALL", "DECLARE", "SET"
]

# Forbidden patterns
FORBIDDEN_PATTERNS = [
    r";\s*\w",  # Multiple statements (semicolon followed by word)
    r"--",      # SQL comments
    r"/\*",     # Block comments start
    r"\*/",     # Block comments end
]


def check_forbidden_keywords(sql: str) -> Tuple[bool, str]:
    """Check if SQL contains forbidden keywords.

    This is a TOOL used by the SQL Validator Sub-Agent.

    Args:
        sql: The SQL query to check

    Returns:
        tuple: (is_valid, error_message)
            - (True, "") if no forbidden keywords found
            - (False, "reason") if forbidden keywords detected
    """
    # Convert to uppercase for comparison
    sql_upper = sql.upper()

    # Check forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            logger.warning(f"Forbidden keyword detected: {keyword}")
            return False, f"Contains forbidden keyword: {keyword}"

    # Check forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, sql):
            logger.warning(f"Forbidden pattern detected: {pattern}")
            return False, f"Contains forbidden pattern: {pattern}"

    # Check for multiple statements (simple check)
    # Allow only one semicolon at the very end
    semicolon_count = sql.count(';')
    if semicolon_count > 1:
        return False, "Multiple statements detected (multiple semicolons)"

    if semicolon_count == 1 and not sql.strip().endswith(';'):
        return False, "Semicolon found in middle of query"

    return True, ""


def parse_sql_query(sql: str) -> Tuple[bool, str]:
    """Parse and validate SQL query structure.

    This is a TOOL used by the SQL Validator Sub-Agent.

    Args:
        sql: The SQL query to parse

    Returns:
        tuple: (is_valid, error_message)
            - (True, "") if SQL is valid
            - (False, "reason") if SQL is invalid
    """
    # Strip whitespace
    sql_clean = sql.strip()

    if not sql_clean:
        return False, "Empty query"

    # Remove trailing semicolon for checks
    if sql_clean.endswith(';'):
        sql_clean = sql_clean[:-1].strip()

    # Convert to uppercase for keyword checking
    sql_upper = sql_clean.upper()

    # Must start with SELECT or WITH (for CTEs)
    if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
        return False, "Query must start with SELECT or WITH"

    # Check for balanced parentheses
    if sql_clean.count('(') != sql_clean.count(')'):
        return False, "Unbalanced parentheses"

    # Check for balanced quotes
    single_quotes = sql_clean.count("'")
    if single_quotes % 2 != 0:
        return False, "Unbalanced single quotes"

    double_quotes = sql_clean.count('"')
    if double_quotes % 2 != 0:
        return False, "Unbalanced double quotes"

    backticks = sql_clean.count('`')
    if backticks % 2 != 0:
        return False, "Unbalanced backticks"

    # Basic structure check - should contain FROM
    if 'FROM' not in sql_upper:
        # Allow simple SELECT queries without FROM (e.g., SELECT 1)
        # but most real queries should have FROM
        logger.warning("Query does not contain FROM clause")

    logger.info("SQL query passed basic validation")
    return True, ""


def validate_sql_security(sql: str) -> Tuple[bool, str]:
    """Complete SQL security validation.

    Combines keyword checking and parsing.
    This is a convenience function that calls both validation tools.

    Args:
        sql: The SQL query to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check forbidden keywords first
    is_valid, error = check_forbidden_keywords(sql)
    if not is_valid:
        return False, error

    # Parse SQL structure
    is_valid, error = parse_sql_query(sql)
    if not is_valid:
        return False, error

    return True, "VALID"
