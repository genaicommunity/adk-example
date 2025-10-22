"""
FinOps Cost Data Analyst - Main Entry Point
Enterprise-grade multi-agent AI system for cloud financial operations.

This is the ADK entry point using the correct LlmAgent pattern.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the root agent
from finops_cost_analyst import root_agent

# Export root_agent for ADK
__all__ = ["root_agent"]

if __name__ == "__main__":
    print("\n" + "="*80)
    print("FinOps Cost Data Analyst Agent - Initialized Successfully!")
    print("="*80)
    print(f"\n Multi-Agent Architecture (ADK LlmAgent):")
    print(f"  ├─ Root Agent: finops_cost_analyst_root")
    print(f"  └─ Sub-Agents (called via tools):")
    print(f"     ├─ Schema Analyst")
    print(f"     ├─ SQL Generator (business logic)")
    print(f"     ├─ SQL Validator (security)")
    print(f"     ├─ BigQuery Executor")
    print(f"     └─ Insight Synthesizer")
    print(f"\n BigQuery Table:")
    print(f"  └─ {os.getenv('BIGQUERY_PROJECT', 'gac-prod-471220')}.{os.getenv('BIGQUERY_DATASET', 'agent_bq_dataset')}.{os.getenv('BIGQUERY_TABLE', 'cost_analysis')}")
    print(f"\n Model: {os.getenv('ROOT_AGENT_MODEL', 'gemini-2.0-flash-exp')}")
    print(f"\n Run: adk web")
    print("="*80 + "\n")
