"""Root Agent - FinOps Cost Data Analyst with Sequential Multi-Agent Workflow.

This is the enterprise-grade root agent following ADK best practices.

Architecture:
    Root Agent (SequentialAgent)
        ↓ orchestrates
    Sub-Agents (sql_generation, sql_validation, query_execution, insight_synthesis)
        ↓ each sub-agent's output goes to next sub-agent via state
    Real Tools (validation_tools, BigQueryToolset, etc.)
"""

import logging
import os
from google.adk.agents import SequentialAgent

from sub_agents import (
    sql_generation_agent,
    sql_validation_agent,
    query_execution_agent,
    insight_synthesis_agent,
)
from prompts import ROOT_AGENT_DESCRIPTION

logger = logging.getLogger(__name__)


# Create root agent with sequential workflow
# Each sub-agent's output feeds into the next via shared state
root_agent = SequentialAgent(
    name="FinOpsCostAnalystOrchestrator",
    description=ROOT_AGENT_DESCRIPTION,
    sub_agents=[
        sql_generation_agent,      # Outputs: state['sql_query']
        sql_validation_agent,       # Uses: state['sql_query'], Outputs: state['validation_result']
        query_execution_agent,      # Uses: state['sql_query'], Outputs: state['query_results']
        insight_synthesis_agent,    # Uses: state['sql_query'] + state['query_results']
    ]
)

logger.info("✓ Root Agent (SequentialAgent) initialized with 4 sub-agents")
