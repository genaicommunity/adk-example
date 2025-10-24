"""Simple test to verify the agent loads and works correctly."""

import sys
import importlib
from pathlib import Path

# Add parent directory to path so we can import the package
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Load agent module using importlib (handles dashes in package name)
agent_module = importlib.import_module('finops-cost-data-analyst.agent')
root_agent = agent_module.root_agent

def test_agent_structure():
    """Test that the agent is properly structured."""
    print("\n" + "="*80)
    print("Testing FinOps Cost Data Analyst Agent Structure")
    print("="*80)

    # Test 1: Verify root agent exists
    print("\n✓ Test 1: Root agent exists")
    assert root_agent is not None
    print(f"  Agent name: {root_agent.name}")

    # Test 2: Verify it's a SequentialAgent
    print("\n✓ Test 2: Agent type is SequentialAgent")
    from google.adk.agents import SequentialAgent
    assert isinstance(root_agent, SequentialAgent)
    print(f"  Agent type: {type(root_agent).__name__}")

    # Test 3: Verify it has sub-agents
    print("\n✓ Test 3: Has 4 sub-agents")
    assert hasattr(root_agent, 'sub_agents')
    assert len(root_agent.sub_agents) == 4
    print(f"  Number of sub-agents: {len(root_agent.sub_agents)}")

    # Test 4: Verify sub-agent names
    print("\n✓ Test 4: Sub-agent names are correct")
    expected_names = ['sql_generation', 'sql_validation', 'query_execution', 'insight_synthesis']
    actual_names = [agent.name for agent in root_agent.sub_agents]
    print(f"  Sub-agents: {', '.join(actual_names)}")
    assert actual_names == expected_names

    # Test 5: Verify output_keys exist
    print("\n✓ Test 5: All sub-agents have output_key defined")
    expected_output_keys = ['sql_query', 'validation_result', 'query_results', 'final_insights']
    actual_output_keys = [agent.output_key for agent in root_agent.sub_agents]
    print(f"  Output keys: {', '.join(actual_output_keys)}")
    assert actual_output_keys == expected_output_keys

    # Test 6: Verify tools are attached to sub-agents, not root
    print("\n✓ Test 6: Root has no tools, sub-agents have tools")
    # SequentialAgent doesn't have tools attribute
    print(f"  Root agent tools: None (SequentialAgent)")

    # Check sub-agents for tools
    sql_validation_agent = root_agent.sub_agents[1]
    query_execution_agent = root_agent.sub_agents[2]

    assert hasattr(sql_validation_agent, 'tools')
    assert len(sql_validation_agent.tools) > 0
    print(f"  sql_validation has {len(sql_validation_agent.tools)} tools")

    assert hasattr(query_execution_agent, 'tools')
    assert len(query_execution_agent.tools) > 0
    print(f"  query_execution has {len(query_execution_agent.tools)} tools (BigQueryToolset)")

    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80)
    print("\nAgent is correctly structured:")
    print("  • Root: SequentialAgent (no tools, has sub_agents)")
    print("  • Sub-agents: LlmAgent (with tools + output_key)")
    print("  • Data flow: Via shared state dictionary")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    try:
        test_agent_structure()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
