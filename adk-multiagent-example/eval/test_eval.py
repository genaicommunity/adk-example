"""Agent Evaluation Tests for Google ADK Multi-Agent System.

Run with: pytest eval/test_eval.py -v

Follows Google ADK pattern from:
github.com/google/adk-samples/python/agents/data-science/eval
"""

import os
import pytest
from dotenv import find_dotenv, load_dotenv

# For now, we'll use a simplified evaluator since google.adk.evaluation
# may require specific setup. This can be replaced with the real
# AgentEvaluator when ready.

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables."""
    load_dotenv(find_dotenv(".env"))


@pytest.mark.asyncio
async def test_eval_main_agent():
    """Test the main coordinator agent's ability via evaluation dataset.

    This test follows Google ADK's AgentEvaluator pattern.
    The test file is structured with:
    - query: User query to test
    - expected_tool_use: Expected agent delegations and tool calls
    - reference: Expected response pattern

    To run with real AgentEvaluator (when configured):
    ```
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    await AgentEvaluator.evaluate(
        "main_agent",
        os.path.join(os.path.dirname(__file__), "eval_data/main_agent.test.json"),
        num_runs=1,
    )
    ```
    """
    # For now, we validate that the test file exists and is structured correctly
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"
    assert test_file.exists(), f"Test file not found: {test_file}"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    # Validate structure
    assert isinstance(test_data, list), "Test data should be a list"
    assert len(test_data) > 0, "Test data should not be empty"

    for item in test_data:
        assert 'query' in item, "Each test case must have a 'query'"
        assert 'expected_tool_use' in item, "Each test case must have 'expected_tool_use'"
        assert 'reference' in item, "Each test case must have 'reference'"

    print(f"\n✅ Loaded {len(test_data)} test cases from evaluation dataset")
    print(f"📊 Test file structure validated successfully")

    # TODO: Integrate with actual agent when ready
    # For production use, uncomment and configure the AgentEvaluator:
    #
    # from google.adk.evaluation.agent_evaluator import AgentEvaluator
    # await AgentEvaluator.evaluate(
    #     "main_agent",
    #     str(test_file),
    #     num_runs=1,
    # )


@pytest.mark.asyncio
async def test_eval_config():
    """Test that evaluation configuration exists and is valid."""
    from pathlib import Path
    import json

    config_file = Path(__file__).parent / "eval_data/test_config.json"
    assert config_file.exists(), f"Config file not found: {config_file}"

    with open(config_file, 'r') as f:
        config = json.load(f)

    assert 'criteria' in config, "Config must have 'criteria'"
    assert 'tool_trajectory_avg_score' in config['criteria']
    assert 'response_match_score' in config['criteria']

    print(f"\n✅ Evaluation config loaded successfully")
    print(f"📊 Criteria: {config['criteria']}")


def test_dataset_structure():
    """Validate the structure of test dataset."""
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    # Check all required fields
    for idx, item in enumerate(test_data):
        assert 'query' in item, f"Test case {idx} missing 'query'"
        assert 'expected_tool_use' in item, f"Test case {idx} missing 'expected_tool_use'"
        assert 'reference' in item, f"Test case {idx} missing 'reference'"

        # Validate expected_tool_use structure
        for tool_use in item['expected_tool_use']:
            assert 'agent_name' in tool_use, f"Tool use in case {idx} missing 'agent_name'"
            assert 'tool_name' in tool_use, f"Tool use in case {idx} missing 'tool_name'"
            assert 'tool_input' in tool_use, f"Tool use in case {idx} missing 'tool_input'"

    print(f"\n✅ Dataset structure validated: {len(test_data)} test cases")


def test_delegation_coverage():
    """Test that dataset covers both sub-agents."""
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    agents_used = set()
    for item in test_data:
        for tool_use in item['expected_tool_use']:
            agents_used.add(tool_use['agent_name'])

    expected_agents = {'time_weather_agent', 'calculator_agent'}
    assert expected_agents.issubset(agents_used), \
        f"Dataset should cover all agents. Missing: {expected_agents - agents_used}"

    print(f"\n✅ Dataset covers all sub-agents: {agents_used}")


def test_tool_coverage():
    """Test that dataset covers all tools."""
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    tools_used = set()
    for item in test_data:
        for tool_use in item['expected_tool_use']:
            tools_used.add(tool_use['tool_name'])

    expected_tools = {'get_current_time', 'get_weather', 'calculate'}
    assert expected_tools.issubset(tools_used), \
        f"Dataset should cover all tools. Missing: {expected_tools - tools_used}"

    print(f"\n✅ Dataset covers all tools: {tools_used}")


def test_multi_domain_queries():
    """Test that dataset includes multi-domain queries."""
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    multi_domain_count = sum(
        1 for item in test_data
        if len(item['expected_tool_use']) > 1
    )

    assert multi_domain_count > 0, "Dataset should include multi-domain queries"
    print(f"\n✅ Dataset includes {multi_domain_count} multi-domain queries")


def test_edge_cases():
    """Test that dataset includes edge cases."""
    import json
    from pathlib import Path

    test_file = Path(__file__).parent / "eval_data/main_agent.test.json"

    with open(test_file, 'r') as f:
        test_data = json.load(f)

    # Look for division by zero test
    has_edge_case = any(
        'divided by 0' in item['query'].lower() or
        'divide by 0' in item['query'].lower() or
        'divide by zero' in item['query'].lower()
        for item in test_data
    )

    assert has_edge_case, "Dataset should include edge cases like division by zero"
    print(f"\n✅ Dataset includes edge case testing")


if __name__ == "__main__":
    # Run pytest programmatically
    pytest.main([__file__, "-v", "--tb=short", "-s"])
