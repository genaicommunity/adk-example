"""Agent tool wrappers - thin layer between root agent and sub-agents.

This file contains async functions that wrap sub-agents for ADK's function calling.

Architecture (CORRECT for ADK):
    Root Agent → Agent Tool Wrappers (this file) → Sub-Agents → Real Tools

Why this pattern in ADK:
    - ADK's LlmAgent uses 'tools' parameter (not 'agents')
    - Sub-agents are wrapped in async functions to be callable as tools
    - Sub-agents themselves use real tools (BigQuery, validation, etc.)

This IS the correct enterprise pattern for ADK v1.16+
"""

import logging
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# Import sub-agents (these have the real tools attached)
from .sub_agents.sql_generator import get_sql_generator_agent
from .sub_agents.sql_validator import get_sql_validator_agent
from .sub_agents.bigquery import get_bigquery_executor_agent
from .sub_agents.insight_synthesizer import get_insight_synthesizer_agent

logger = logging.getLogger(__name__)


async def call_sql_generator(question: str, tool_context: ToolContext) -> str:
    """Call SQL Generator Sub-Agent.

    This is a thin wrapper. The real work happens in the sub-agent.

    Args:
        question: User's natural language question
        tool_context: Tool execution context

    Returns:
        str: Generated SQL query
    """
    logger.debug("Calling SQL Generator sub-agent")

    # Create sub-agent (has no tools - schema hardcoded)
    agent = get_sql_generator_agent()

    # Wrap as tool for ADK
    agent_tool = AgentTool(agent=agent)

    # Execute
    request = f"Generate SQL for: {question}"
    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["sql_query"] = output
    return output


async def call_sql_validator(sql_query: str, tool_context: ToolContext) -> str:
    """Call SQL Validator Sub-Agent.

    This sub-agent USES TOOLS: check_forbidden_keywords, parse_sql_query

    Args:
        sql_query: SQL query to validate
        tool_context: Tool execution context

    Returns:
        str: "VALID" or "INVALID: reason"
    """
    logger.debug("Calling SQL Validator sub-agent")

    # Create sub-agent (HAS validation tools attached)
    agent = get_sql_validator_agent()

    # Wrap as tool for ADK
    agent_tool = AgentTool(agent=agent)

    # Execute
    request = f"Validate this SQL query:\n\n{sql_query}"
    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["validation_result"] = output
    return output


async def call_bigquery_executor(sql_query: str, tool_context: ToolContext) -> str:
    """Call BigQuery Executor Sub-Agent.

    This sub-agent USES TOOLS: execute_sql (from ADK BigQueryToolset)

    Args:
        sql_query: Validated SQL query to execute
        tool_context: Tool execution context

    Returns:
        str: Query results
    """
    logger.debug("Calling BigQuery Executor sub-agent")

    # Create sub-agent (HAS BigQueryToolset attached)
    agent = get_bigquery_executor_agent()

    # Wrap as tool for ADK
    agent_tool = AgentTool(agent=agent)

    # Execute
    request = f"Execute this SQL query:\n\n{sql_query}"
    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["query_results"] = output
    return output


async def call_insight_synthesizer(question: str, tool_context: ToolContext) -> str:
    """Call Insight Synthesizer Sub-Agent.

    This sub-agent formats results into insights (no tools needed).

    Args:
        question: Original user question
        tool_context: Tool execution context

    Returns:
        str: Formatted business insights
    """
    logger.debug("Calling Insight Synthesizer sub-agent")

    # Create sub-agent (no tools needed)
    agent = get_insight_synthesizer_agent()

    # Wrap as tool for ADK
    agent_tool = AgentTool(agent=agent)

    # Get previous results from state
    sql = tool_context.state.get("sql_query", "SQL not available")
    results = tool_context.state.get("query_results", "Results not available")

    # Execute
    request = f"""
User Question: {question}

SQL Query Executed:
{sql}

Query Results:
{results}

Format these into business insights.
"""
    output = await agent_tool.run_async(
        args={"request": request},
        tool_context=tool_context
    )

    tool_context.state["insights"] = output
    return output
