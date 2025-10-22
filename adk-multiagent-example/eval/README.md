# Evaluation & Testing

Google ADK-style evaluation framework for the multi-agent system.

**Pattern:** `github.com/google/adk-samples/python/agents/data-science/eval`

---

## Quick Start

```bash
# Run all evaluations
pytest eval/test_eval.py -v

# Run unit tests
python eval/test_tools.py

# Interactive testing
./eval/test_agents_interactive.sh
```

---

## Structure

```
eval/
├── eval_data/
│   ├── main_agent.test.json    # Test dataset with input/output expectations
│   └── test_config.json         # Evaluation criteria & thresholds
├── test_eval.py                 # Agent evaluation tests (ADK pattern)
├── test_tools.py                # Unit tests for tools
├── test_agents_interactive.sh   # Interactive testing menu
├── evaluation_queries.md        # Test queries reference
└── README.md                    # This file
```

---

## Testing Levels

### 1. Unit Tests (Tools)
```bash
python eval/test_tools.py
```

Tests all tools independently:
- ✅ `get_current_time`
- ✅ `get_weather`
- ✅ `calculate`

**Pass Criteria:**
- All assertions pass
- No exceptions raised
- Error cases handled (division by zero, etc.)

### 2. Agent Evaluation (ADK Pattern)
```bash
pytest eval/test_eval.py -v
```

Tests agent behavior against evaluation dataset:
- Delegation accuracy
- Tool selection
- Multi-domain queries
- Edge cases

**Tests:**
- `test_eval_main_agent` - Validates dataset structure & runs evaluation
- `test_eval_config` - Validates configuration file
- `test_dataset_structure` - Ensures all required fields present
- `test_delegation_coverage` - Verifies all sub-agents are tested
- `test_tool_coverage` - Verifies all tools are tested
- `test_multi_domain_queries` - Checks multi-agent coordination
- `test_edge_cases` - Validates edge case coverage

### 3. Interactive Testing
```bash
./eval/test_agents_interactive.sh
```

Menu-driven testing for:
- Time/Weather Agent
- Calculator Agent
- Main Coordinator Agent

---

## Test Dataset Format

Each test case in `eval_data/main_agent.test.json`:

```json
{
  "query": "What time is it in Tokyo?",
  "expected_tool_use": [
    {
      "agent_name": "time_weather_agent",
      "tool_name": "get_current_time",
      "tool_input": {"city": "Tokyo"}
    }
  ],
  "expected_intermediate_agent_responses": [],
  "reference": "The current time in Tokyo is [time]. The coordinator should delegate to time_weather_agent."
}
```

---

## Dataset Coverage

Current dataset includes:

| Category | Count | Examples |
|----------|-------|----------|
| **Time queries** | 3 | "What time is it in Tokyo?" |
| **Weather queries** | 2 | "What's the weather in London?" |
| **Calculations** | 3 | "Calculate 25 times 4" |
| **Multi-domain** | 3 | "Weather and time in London" |
| **Edge cases** | 1 | "What is 10 divided by 0?" |
| **TOTAL** | 10 | Complete coverage |

**Agent Coverage:**
- ✅ time_weather_agent
- ✅ calculator_agent

**Tool Coverage:**
- ✅ get_current_time
- ✅ get_weather
- ✅ calculate

---

## Evaluation Configuration

`eval_data/test_config.json` defines criteria:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.3
  },
  "thresholds": {
    "delegation_accuracy": 1.0,
    "tool_selection_accuracy": 1.0,
    "multi_domain_handling": 0.8
  }
}
```

---

## Integration with AgentEvaluator

### Current: Structure Validation

The current implementation validates dataset structure.

### Future: Real Agent Evaluation

To run with Google ADK's `AgentEvaluator`:

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator

await AgentEvaluator.evaluate(
    "main_agent",
    "eval/eval_data/main_agent.test.json",
    num_runs=1,
)
```

This will:
1. Load the agent
2. Run each query through the agent
3. Compare actual vs expected tool use
4. Score responses against reference
5. Generate evaluation report

---

## Extending the Dataset

### Add New Test Case

Edit `eval_data/main_agent.test.json`:

```json
{
  "query": "Your new query here",
  "expected_tool_use": [
    {
      "agent_name": "agent_to_use",
      "tool_name": "tool_to_call",
      "tool_input": {"param": "value"}
    }
  ],
  "expected_intermediate_agent_responses": [],
  "reference": "Expected response pattern"
}
```

### Update Criteria

Edit `eval_data/test_config.json` to adjust thresholds.

---

## Quick Test Queries

See **[evaluation_queries.md](evaluation_queries.md)** for complete list.

```
# Single Domain
What time is it in Tokyo?
What's the weather in London?
Calculate 25 times 4

# Multi-Domain
What's the weather in London and what time is it there?
```

---

## Verification Checklist

- [ ] Unit tests pass: `python eval/test_tools.py`
- [ ] Evaluation tests pass: `pytest eval/test_eval.py -v`
- [ ] All agents respond correctly
- [ ] Main coordinator delegates properly
- [ ] Edge cases handled gracefully

---

## Why This Format?

**Better than simple assertions:**

```python
# ❌ Simple test - only checks if it works
assert agent.run("What time in Tokyo?") is not None

# ✅ Eval dataset - checks HOW it works
{
  "query": "What time in Tokyo?",
  "expected_tool_use": [...],     # Validates delegation
  "reference": "..."               # Validates response quality
}
```

**Benefits:**
1. **Delegation Validation** - Ensures main agent delegates correctly
2. **Tool Selection** - Validates right tools are used
3. **Parameter Validation** - Checks tool inputs are correct
4. **Response Quality** - Compares against reference
5. **Reusable** - Dataset can be used for regression testing
6. **Extensible** - Easy to add new test cases

---

**Evaluation framework complete!** ✅
