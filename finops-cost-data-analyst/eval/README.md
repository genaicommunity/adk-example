# Evaluation Framework

This directory contains test cases for evaluating the FinOps Cost Data Analyst multi-agent system.

## Structure

```
eval/
└── eval_data/
    └── simple.test.json  # Test cases for basic functionality
```

## Test Format

Each test case in `simple.test.json` follows this format:

```json
{
  "query": "User question to the agent",
  "expected_tool_use": [
    {
      "tool_name": "call_sql_generation_agent",
      "tool_input": {"question": "..."}
    }
  ],
  "expected_intermediate_agent_responses": [],
  "reference": "Expected output or behavior"
}
```

## Running Tests

The test cases validate:
1. **Sequential Workflow**: SQL Generation → Validation → Execution → Synthesis
2. **Tool Usage**: Correct tools called in proper sequence
3. **Output Quality**: Business insights match expected format

## Test Cases

1. **Data Discovery** - Validates agent knows its data sources
2. **Top Applications** - Tests full sequential workflow
3. **Cloud Cost Breakdown** - Tests time-based queries

## Adding New Tests

Add new test cases to `simple.test.json` following the established format. Ensure:
- Clear query intent
- Expected tool sequence
- Reference output for validation
