# FinOps Agent - API Client Examples

This directory contains examples demonstrating how to use **agent-card.json** and **a2a-spec.json** for agent-to-agent communication.

---

## Files

| File | Purpose | Uses Spec? |
|------|---------|------------|
| `api_client_spec.py` | ✅ **Spec-driven Python client** | ✅ Yes - Recommended |
| `api_test_spec.sh` | ✅ **Spec-driven shell tests** | ✅ Yes - Recommended |
| `spec_utils.py` | ✅ **Spec browsing utility** | ✅ Yes |
| `api_client.py` | Basic Python client | ❌ No (hardcoded) |
| `api_test.sh` | Basic shell tests | ❌ No (hardcoded) |

**Recommendation**: Use the `*_spec.*` versions - they read from JSON specs and are more maintainable!

---

## Quick Start

### 1. Start the Server

```bash
cd /Users/gurukallam/projects/google-adk-agents
adk web --port 8000
```

### 2. Browse Agent Specs

```bash
# Show agent info
python3 examples/spec_utils.py info

# Show all intents with examples
python3 examples/spec_utils.py intents

# Show request templates
python3 examples/spec_utils.py templates

# Show everything
python3 examples/spec_utils.py all
```

### 3. Run Spec-Driven Tests

**Python:**
```bash
python3 examples/api_client_spec.py
```

**Shell:**
```bash
./examples/api_test_spec.sh
```

---

## Spec-Driven Python Client (api_client_spec.py)

### Features

✅ **Loads specs automatically** - Reads agent-card.json and a2a-spec.json
✅ **Discovers capabilities** - Lists all supported intents
✅ **Uses templates** - Builds requests from spec templates
✅ **Validates requests** - Checks against JSON schema
✅ **Parses responses** - Extracts structured data using spec patterns

### Basic Usage

```python
from api_client_spec import FinOpsAgentClient

# Initialize (automatically loads specs)
client = FinOpsAgentClient()

# Query agent
result = client.query("What is the total cost for FY26?")
print(result['answer'])
```

### Discover Capabilities

```python
# Get all capabilities
capabilities = client.get_capabilities()
print(f"Agent can: {capabilities}")

# Get all intents
intents = client.get_intents()
for intent_name, intent_data in intents.items():
    print(f"{intent_name}: {intent_data['description']}")
```

### Query by Intent

```python
# Use example from COST_AGGREGATION intent
result = client.query_from_intent(
    intent="COST_AGGREGATION",
    example_index=0  # Use first example
)
print(result['answer'])
```

### Run Predefined Examples

```python
# List available examples
examples = client.get_example_requests()
print(f"Available: {list(examples.keys())}")

# Run "totalCost" example
result = client.run_example("totalCost")
print(result['answer'])
```

### Parse Structured Data

```python
# Query for ranked list
result = client.query("What are the top 5 applications by cost?")

# Parse using spec pattern
items = client.parse_ranked_list(result['answer'])
for item in items:
    print(f"{item['rank']}. {item['name']}: ${item['cost']:,.2f}")

# Parse cost from text
cost = client.parse_cost(result['answer'])
print(f"Parsed cost: ${cost:,.2f}")
```

### Validate Requests

```python
# Build request from template
request = client.build_request(
    question="What is the total cost?",
    user_id="my-agent",
    session_id="session-123"
)

# Validate against schema
is_valid, error = client.validate_request(request)
if is_valid:
    print("✅ Request is valid!")
else:
    print(f"❌ Invalid: {error}")
```

### Examples Included

Run the script to see 5 complete examples:

```bash
python3 examples/api_client_spec.py
```

1. **Discover Capabilities** - Load and display agent capabilities from spec
2. **Query by Intent** - Use intent examples from agent card
3. **Run Predefined Example** - Execute examples from agent card
4. **Validate Request** - Validate using JSON schema
5. **Parse Response** - Extract structured data using spec patterns

---

## Spec-Driven Shell Tests (api_test_spec.sh)

### Features

✅ **Reads agent-card.json** - Loads metadata, intents, examples
✅ **Reads a2a-spec.json** - Uses templates and use cases
✅ **Comprehensive tests** - Tests all intents and examples
✅ **Color output** - Easy to read results

### Usage

```bash
./examples/api_test_spec.sh
```

### What It Tests

1. **Server Status** - Checks if ADK server is running
2. **Agent Metadata** - Loads and displays agent info from spec
3. **Example Queries** - Runs examples from agent-card.json
4. **Intent Testing** - Tests each intent with example queries
5. **Template Usage** - Uses query templates from a2a-spec.json
6. **Schema Validation** - Validates request structure
7. **Use Cases** - Executes use cases from a2a-spec.json

### Sample Output

```
============================================================
FinOps Cost Data Analyst - Spec-Driven API Test
============================================================

Base URL:     http://localhost:8000
Agent Card:   /path/to/agent-card.json
A2A Spec:     /path/to/a2a-spec.json

✅ Loaded Agent Spec
   Name:    finops-cost-data-analyst
   Display: FinOps Cost Data Analyst
   Version: 1.0.0

📋 Capabilities:
   - cost-aggregation
   - cost-breakdown
   - cost-ranking
   - trend-analysis
   - anomaly-detection
   - forecasting

🎯 Supported Intents:
   - COST_AGGREGATION: Calculate total, average, or sum of costs
   - COST_BREAKDOWN: Break down costs by dimensions
   ...
```

---

## Spec Utilities (spec_utils.py)

### Features

✅ **Browse specs** - Explore agent-card.json and a2a-spec.json
✅ **Show capabilities** - List all intents, templates, use cases
✅ **Generate requests** - Create requests from templates
✅ **No server required** - Works offline

### Usage

```bash
# Show agent info and capabilities
python3 examples/spec_utils.py info

# Show all intents with examples
python3 examples/spec_utils.py intents

# Show request templates
python3 examples/spec_utils.py templates

# Show use cases
python3 examples/spec_utils.py usecases

# Show predefined examples
python3 examples/spec_utils.py examples

# Show everything
python3 examples/spec_utils.py all
```

### Sample Output

```bash
$ python3 examples/spec_utils.py intents

Supported Intents:

  COST_AGGREGATION:
    Description: Calculate total, average, or sum of costs
    Output Type: single-value
    Examples:
      - What is the total cost for FY26?
      - What is the average daily cost?
      - Sum of all costs for February 2025

  COST_RANKING:
    Description: Rank resources by cost (top/bottom N)
    Output Type: ranked-list
    Examples:
      - What are the top 10 applications by cost?
      - Show me the 5 most expensive cloud services
      - Which applications cost the least?
```

### Use in Your Code

```python
from spec_utils import load_specs, get_template, show_agent_info

# Load specs
agent_card, a2a_spec = load_specs()

# Show agent info
show_agent_info(agent_card)

# Get a template
template = get_template(a2a_spec, "basicQuery")
print(json.dumps(template, indent=2))
```

---

## Comparison: Basic vs Spec-Driven

### Basic Clients (api_client.py, api_test.sh)

**Pros:**
- ✅ Simple and straightforward
- ✅ No dependencies

**Cons:**
- ❌ Hardcoded agent name
- ❌ No capability discovery
- ❌ No request validation
- ❌ Manual request building
- ❌ Hardcoded examples

**Use when:** Quick testing, simple integration

### Spec-Driven Clients (api_client_spec.py, api_test_spec.sh)

**Pros:**
- ✅ Reads from spec files (single source of truth)
- ✅ Automatic capability discovery
- ✅ Request validation against schema
- ✅ Uses templates from spec
- ✅ Examples from spec
- ✅ Easier to maintain

**Cons:**
- ❌ Requires jsonschema library (optional)
- ❌ Slightly more complex

**Use when:** Production integration, A2A communication, maintainable code

---

## Real-World Integration Examples

### Budget Agent Integration

```python
from api_client_spec import FinOpsAgentClient

class BudgetAgent:
    def __init__(self):
        self.finops_client = FinOpsAgentClient()

    def analyze_variance(self):
        # Discover if FinOps agent supports cost aggregation
        intents = self.finops_client.get_intents()
        if 'COST_AGGREGATION' not in intents:
            raise Exception("FinOps agent doesn't support cost aggregation")

        # Query using intent example
        result = self.finops_client.query_from_intent(
            intent="COST_AGGREGATION",
            user_id="budget-agent"
        )

        # Parse cost
        actual_cost = self.finops_client.parse_cost(result['answer'])

        # Get budget from database
        budget = self.get_budget_from_db()

        # Calculate variance
        return {
            "actual": actual_cost,
            "budget": budget,
            "variance": budget - actual_cost
        }
```

### Dashboard Service Integration

```python
from api_client_spec import FinOpsAgentClient
from concurrent.futures import ThreadPoolExecutor

class DashboardService:
    def __init__(self):
        self.client = FinOpsAgentClient()

    def get_dashboard_data(self):
        # Get example queries from spec
        intents = self.client.get_intents()

        queries = [
            intents['COST_AGGREGATION']['examples'][0],  # Total cost
            intents['COST_RANKING']['examples'][0],      # Top apps
            intents['COST_BREAKDOWN']['examples'][0],    # Breakdown
        ]

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    self.client.query,
                    question=q,
                    user_id="dashboard",
                    session_id=f"dash-{i}"
                )
                for i, q in enumerate(queries)
            ]

            results = [f.result() for f in futures]

        return {
            "total_cost": results[0]['answer'],
            "top_apps": results[1]['answer'],
            "breakdown": results[2]['answer']
        }
```

---

## Dependencies

### Required

- Python 3.11+
- `requests` library
- `jq` (for shell scripts)

### Optional

- `jsonschema` - For request validation (highly recommended)

**Install:**
```bash
pip install requests jsonschema
```

---

## Troubleshooting

### "jsonschema not installed"

**Solution:**
```bash
pip install jsonschema
```

The client still works without it, but request validation is disabled.

### "agent-card.json not found"

**Cause:** Running from wrong directory

**Solution:**
```bash
# Run from examples/ directory
cd finops-cost-data-analyst/examples
python3 api_client_spec.py

# Or from parent
cd finops-cost-data-analyst
python3 examples/api_client_spec.py
```

### "Server not running"

**Solution:**
```bash
cd /Users/gurukallam/projects/google-adk-agents
adk web --port 8000
```

---

## Best Practices

### 1. Use Spec-Driven Clients

✅ **Do:**
```python
from api_client_spec import FinOpsAgentClient
client = FinOpsAgentClient()  # Reads specs
```

❌ **Don't:**
```python
# Hardcoding agent name and endpoints
client = SomeClient(agent_name="finops-cost-data-analyst")
```

### 2. Discover Capabilities First

✅ **Do:**
```python
client = FinOpsAgentClient()
if 'COST_AGGREGATION' in client.get_intents():
    result = client.query_from_intent('COST_AGGREGATION')
```

❌ **Don't:**
```python
# Assuming agent has capability without checking
result = client.query("What is the cost?")
```

### 3. Use Templates

✅ **Do:**
```python
request = client.build_request(
    question="What is the total cost?",
    template="basicQuery"
)
```

❌ **Don't:**
```python
# Manually building requests
request = {
    "appName": "finops-cost-data-analyst",
    "userId": "me",
    # ... manual construction
}
```

### 4. Validate Requests

✅ **Do:**
```python
request = client.build_request(...)
is_valid, error = client.validate_request(request)
if is_valid:
    response = requests.post(url, json=request)
```

❌ **Don't:**
```python
# Sending without validation
response = requests.post(url, json=request)
```

---

## Next Steps

1. **Start server**: `adk web --port 8000`
2. **Browse specs**: `python3 examples/spec_utils.py all`
3. **Run examples**: `python3 examples/api_client_spec.py`
4. **Test all**: `./examples/api_test_spec.sh`
5. **Integrate**: Use `api_client_spec.py` as template

---

## Summary

| Feature | Basic Client | Spec-Driven Client |
|---------|-------------|-------------------|
| Loads specs | ❌ | ✅ |
| Capability discovery | ❌ | ✅ |
| Request validation | ❌ | ✅ |
| Uses templates | ❌ | ✅ |
| Response parsing | ✅ | ✅ |
| Maintainability | ⚠️ Low | ✅ High |

**Recommendation**: Use spec-driven clients for all production integrations!

---

**For more information:**
- Agent Card: `../agent-card.json`
- A2A Spec: `../a2a-spec.json`
- Spec README: `../A2A_SPEC_README.md`
- API Guide: `../docs/API_GUIDE.md`
