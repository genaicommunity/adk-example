"""Tools for calling sub-agents from the root agent."""

import logging
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.sql_generator import get_sql_generator_agent
from .sub_agents.sql_validator import get_sql_validator_agent
from .sub_agents.bigquery import get_bigquery_executor_agent
from .sub_agents.insight_synthesizer import get_insight_synthesizer_agent

logger = logging.getLogger(__name__)


async def call_sql_generator(question: str, tool_context: ToolContext) -> str:
    """
    Call the SQL Generator agent to convert natural language to SQL.

    Schema is now hardcoded in the SQL generator prompt for performance.

    Args:
        question: The user's natural language question
        tool_context: The tool context for agent execution

    Returns:
        str: The generated SQL query
    """
    logger.debug("call_sql_generator: %s", question)

    agent = get_sql_generator_agent()
    agent_tool = AgentTool(agent=agent)

    request = f"""
User Question: {question}

Generate the appropriate BigQuery SQL query for this question.
Return ONLY the SQL query, no explanations.
"""

    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["sql_query"] = output
    return output


async def call_sql_validator(sql_query: str, tool_context: ToolContext) -> str:
    """
    Call the SQL Validator agent to validate SQL security.

    Args:
        sql_query: The SQL query to validate
        tool_context: The tool context for agent execution

    Returns:
        str: "VALID" or "INVALID: reason"
    """
    logger.debug("call_sql_validator")

    agent = get_sql_validator_agent()
    agent_tool = AgentTool(agent=agent)

    request = f"""
Validate this SQL query for security:

{sql_query}

Return ONLY "VALID" or "INVALID: reason"
"""

    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["validation_result"] = output
    return output


async def call_bigquery_executor(sql_query: str, tool_context: ToolContext) -> str:
    """
    Call the BigQuery Executor agent to run a validated SQL query.

    Args:
        sql_query: The validated SQL query to execute
        tool_context: The tool context for agent execution

    Returns:
        str: The query results
    """
    logger.debug("call_bigquery_executor")

    agent = get_bigquery_executor_agent()
    agent_tool = AgentTool(agent=agent)

    request = f"""
Execute this SQL query on BigQuery:

{sql_query}
"""

    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["query_results"] = output
    return output


async def call_insight_synthesizer(question: str, tool_context: ToolContext) -> str:
    """
    Call the Insight Synthesizer agent to format results into insights.

    Args:
        question: The original user question
        tool_context: The tool context for agent execution

    Returns:
        str: Formatted business insights
    """
    logger.debug("call_insight_synthesizer: %s", question)

    agent = get_insight_synthesizer_agent()
    agent_tool = AgentTool(agent=agent)

    # Get SQL and results from state
    sql = tool_context.state.get("sql_query", "SQL not available")
    results = tool_context.state.get("query_results", "Results not available")

    request = f"""
User Question: {question}

SQL Query Executed:
{sql}

Query Results:
{results}

Format these results into clear, actionable business insights.
"""

    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["insights"] = output
    return output
