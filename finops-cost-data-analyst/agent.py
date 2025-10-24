"""Root Agent - FinOps Cost Data Analyst with Sequential Multi-Agent Workflow.

This is the enterprise-grade root agent following ADK best practices.
All sub-agents are defined in sub_agents.py for better organization.

Architecture:
    Root Agent (SequentialAgent) - defined here
        ↓ orchestrates
    Sub-Agents (sql_generation, sql_validation, query_execution, insight_synthesis) - in sub_agents.py
        ↓ each sub-agent's output goes to next sub-agent via state
    Tools (from _tools package) - in _tools/
"""

import logging

from google.adk.agents import SequentialAgent

from .prompts import ROOT_AGENT_DESCRIPTION
from .sub_agents import (
    sql_generation_agent,
    sql_validation_agent,
    query_execution_agent,
    insight_synthesis_agent,
)

logger = logging.getLogger(__name__)


# ============================================================================
# ROOT AGENT - Sequential Orchestrator
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
        insight_synthesis_agent,    # Uses: state['query_results'], Outputs: state['final_insights']
                                    # LAST agent - its output will be shown to user
    ],
)

logger.info("✓ Root Agent (SequentialAgent) initialized with 4 sub-agents")

# Export for ADK
__all__ = ["root_agent"]
