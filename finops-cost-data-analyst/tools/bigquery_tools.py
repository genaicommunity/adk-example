"""BigQuery tools - actual functions that interact with BigQuery.

These tools are used by sub-agents to perform BigQuery operations.
"""

import logging
import os
from google.cloud import bigquery
from typing import Dict, Any

logger = logging.getLogger(__name__)


def execute_bigquery_query(sql: str) -> str:
    """Execute a SQL query on BigQuery.

    This is a TOOL used by the BigQuery Executor Sub-Agent.

    Args:
        sql: The SQL query to execute

    Returns:
        str: Query results formatted as text, or error message
    """
    try:
        # Initialize BigQuery client
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("BIGQUERY_PROJECT")

        if not credentials_path:
            return "ERROR: GOOGLE_APPLICATION_CREDENTIALS not set"

        if not project_id:
            return "ERROR: BIGQUERY_PROJECT not set"

        client = bigquery.Client.from_service_account_json(
            credentials_path,
            project=project_id
        )

        logger.info(f"Executing BigQuery query: {sql[:100]}...")

        # Execute query
        query_job = client.query(sql)
        results = query_job.result()

        # Format results
        if results.total_rows == 0:
            return "No results found"

        # Get column names
        columns = [field.name for field in results.schema]

        # Build result string
        output_lines = []

        # Header
        output_lines.append("\t".join(columns))

        # Rows
        for row in results:
            row_values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
            output_lines.append("\t".join(row_values))

        result_text = "\n".join(output_lines)

        logger.info(f"Query returned {results.total_rows} rows")

        return result_text

    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        logger.error(f"BigQuery execution error: {error_msg}")
        return error_msg


def describe_bigquery_table(table_name: str) -> Dict[str, Any]:
    """Describe a BigQuery table schema.

    This tool is currently NOT USED (schema is hardcoded for performance).
    Kept for future use if dynamic schema lookup is needed.

    Args:
        table_name: Fully qualified table name (project.dataset.table)

    Returns:
        dict: Table schema information
    """
    try:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("BIGQUERY_PROJECT")

        client = bigquery.Client.from_service_account_json(
            credentials_path,
            project=project_id
        )

        table = client.get_table(table_name)

        schema_info = {
            "table": table_name,
            "columns": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                }
                for field in table.schema
            ],
            "num_rows": table.num_rows,
            "partitioning": str(table.time_partitioning) if table.time_partitioning else None,
            "clustering": table.clustering_fields if table.clustering_fields else None
        }

        return schema_info

    except Exception as e:
        logger.error(f"Error describing table: {str(e)}")
        return {"error": str(e)}
