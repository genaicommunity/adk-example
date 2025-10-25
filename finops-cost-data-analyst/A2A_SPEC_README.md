# A2A Communication Specifications - README

**Agent Card and A2A JSON Specifications for FinOps Cost Data Analyst**

---

## Overview

This directory contains **Agent Card** and **A2A Communication Specifications** that describe:
- ✅ What the agent can do (capabilities & intents)
- ✅ How to communicate with it (request/response schemas)
- ✅ Example queries and responses
- ✅ Integration patterns for other agents

---

## Files

| File | Purpose |
|------|---------|
| `agent-card.json` | **Agent Card/Manifest** - Complete agent specification |
| `a2a-spec.json` | **A2A Communication Spec** - Request/response templates & integration examples |
| `A2A_SPEC_README.md` | This file - How to use the specifications |

---

## Quick Start for Agent Developers

### Step 1: Read the Agent Card

```bash
cat agent-card.json | jq '.agentCard.metadata'
```

**What you'll learn:**
- Agent name and description
- Capabilities and supported intents
- API endpoints
- Request/response schemas

### Step 2: Choose an Intent

```bash
cat agent-card.json | jq '.agentCard.intents'
```

**Available Intents:**
1. `COST_AGGREGATION` - Total, average, sum of costs
2. `COST_BREAKDOWN` - Break down by dimension (app, cloud, etc.)
3. `COST_RANKING` - Top/bottom N resources by cost
4. `TREND_ANALYSIS` - Cost trends over time
5. `ANOMALY_DETECTION` - Unusual spending patterns
6. `SAMPLE_DATA` - Random cost records

### Step 3: Use a Template

```bash
cat a2a-spec.json | jq '.templates.basicQuery.example'
```

**Copy and modify the template:**
```json
{
  "appName": "finops-cost-data-analyst",
  "userId": "your-agent-id",
  "sessionId": "your-session-id",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "What is the total cost for FY26?"}]
  }
}
```

### Step 4: Send Request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

## Agent Card Structure

### Metadata
```json
{
  "name": "finops-cost-data-analyst",
  "displayName": "FinOps Cost Data Analyst",
  "description": "Analyzes cloud cost data...",
  "version": "1.0.0",
  "tags": ["finops", "cost-analysis", "bigquery"]
}
```

### Capabilities
```json
{
  "primary": [
    "cost-aggregation",
    "cost-breakdown",
    "cost-ranking",
    "trend-analysis",
    "anomaly-detection",
    "forecasting"
  ],
  "timePeriods": {
    "defaultPeriod": "FY26 YTD",
    "fiscalYears": {
      "FY26": {"start": "2025-02-01", "end": "2026-01-31"}
    }
  }
}
```

### Intents (with Examples)
```json
{
  "COST_AGGREGATION": {
    "description": "Calculate total, average, or sum of costs",
    "examples": [
      "What is the total cost for FY26?",
      "What is the average daily cost?"
    ],
    "outputType": "single-value"
  }
}
```

### Request Schema
```json
{
  "type": "object",
  "required": ["appName", "userId", "sessionId", "newMessage"],
  "properties": {
    "appName": {"type": "string", "const": "finops-cost-data-analyst"},
    "userId": {"type": "string"},
    "sessionId": {"type": "string"},
    "newMessage": {
      "role": "user",
      "parts": [{"text": "your question"}]
    }
  }
}
```

### Response Schema
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "type": "agent_output",
      "content": {
        "role": "model",
        "parts": [{"text": "Agent's answer"}]
      }
    }
  }
}
```

---

## A2A Spec Structure

### Request Templates

**Basic Query Template:**
```json
{
  "template": {
    "appName": "finops-cost-data-analyst",
    "userId": "{{CALLING_AGENT_ID}}",
    "sessionId": "{{SESSION_ID}}",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "{{QUESTION}}"}]
    }
  }
}
```

**Parameterized Query Templates:**
```json
{
  "queryTemplates": {
    "totalCostByPeriod": "What is the total cost for {{PERIOD}}?",
    "topNByDimension": "What are the top {{N}} {{DIMENSION}} by cost?",
    "costBreakdown": "What is the cost breakdown by {{DIMENSION}}?"
  }
}
```

### Use Cases

**Budget Agent Example:**
```json
{
  "scenario": "Budget Agent queries actual costs",
  "workflow": [
    {
      "step": 1,
      "action": "Query total cost",
      "request": {
        "appName": "finops-cost-data-analyst",
        "userId": "budget-agent",
        "newMessage": {
          "role": "user",
          "parts": [{"text": "What is the total cost for FY26?"}]
        }
      }
    },
    {
      "step": 2,
      "action": "Compare with budget and calculate variance"
    }
  ]
}
```

### Integration Examples

**Python:**
```python
import requests

class FinOpsClient:
    def query(self, question, user_id, session_id):
        payload = {
            "appName": "finops-cost-data-analyst",
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": question}]
            }
        }
        response = requests.post(
            "http://localhost:8000/run",
            json=payload
        )
        return response.json()[0]["content"]["parts"][0]["text"]
```

---

## Common Use Cases

### 1. Budget Variance Analysis
```python
# Budget Agent queries FinOps Agent
cost_response = finops_client.query(
    question="What is the total cost for FY26?",
    user_id="budget-agent",
    session_id="budget-session-001"
)

# Parse cost from response
actual_cost = parse_cost(cost_response)
budget = get_budget_from_db()
variance = budget - actual_cost
```

### 2. Daily Monitoring
```bash
#!/bin/bash
# Cron job: Daily cost monitoring

answer=$(curl -s -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "monitoring-agent",
    "sessionId": "daily-'$(date +%Y%m%d)'",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "Find cost anomalies in the last 24 hours"}]
    }
  }' | jq -r '.[].content.parts[0].text')

# Send alerts if anomalies found
echo "$answer" | grep -q "anomaly" && send_alert "$answer"
```

### 3. Dashboard Backend
```python
# Dashboard service queries multiple metrics in parallel
from concurrent.futures import ThreadPoolExecutor

def get_dashboard_data():
    queries = [
        "What is the total cost for FY26?",
        "What are the top 10 applications by cost?",
        "What is the cost breakdown by cloud provider?"
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                finops_client.query,
                question=q,
                user_id="dashboard",
                session_id=f"dash-{i}"
            )
            for i, q in enumerate(queries)
        ]

        results = [f.result() for f in futures]

    return {
        "total_cost": results[0],
        "top_apps": results[1],
        "cloud_breakdown": results[2]
    }
```

### 4. Automated Reporting
```python
# Weekly report generation
def generate_weekly_report():
    session_id = f"weekly-report-{datetime.now().strftime('%Y%m%d')}"

    # Query 1: Weekly total
    total = finops_client.query(
        "What is the total cost for the last 7 days?",
        user_id="report-agent",
        session_id=session_id
    )

    # Query 2: Top spenders (same session for context)
    top_apps = finops_client.query(
        "What are the top 10 applications by cost?",
        user_id="report-agent",
        session_id=session_id  # Same session!
    )

    # Generate PDF and email
    report = create_pdf_report(total, top_apps)
    send_email(report)
```

---

## Response Handling

### Extract Answer from Response

**Python:**
```python
def extract_answer(response_json):
    """Extract text answer from agent response."""
    for event in response_json:
        if event.get("type") == "agent_output":
            return event["content"]["parts"][0]["text"]
    return None
```

**JavaScript:**
```javascript
function extractAnswer(responseJson) {
  const outputEvent = responseJson.find(e => e.type === "agent_output");
  return outputEvent?.content?.parts?.[0]?.text || null;
}
```

### Parse Structured Data

**Parse costs from natural language:**
```python
import re

def parse_cost(text):
    """Extract dollar amount from text."""
    match = re.search(r'\$([0-9,]+(?:\.[0-9]{2})?)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

# Example
response = "The total cost for FY26 YTD is $15,234,567.89"
cost = parse_cost(response)  # 15234567.89
```

**Parse ranked list:**
```python
def parse_ranked_list(text):
    """Parse ranked list of applications with costs."""
    pattern = r'^\d+\.\s+\*\*(.+?)\*\*\s+-\s+\$([0-9,]+(?:\.[0-9]{2})?)'
    items = []

    for line in text.split('\n'):
        match = re.match(pattern, line)
        if match:
            name = match.group(1)
            cost = float(match.group(2).replace(',', ''))
            items.append({"name": name, "cost": cost})

    return items
```

---

## Error Handling

### Common Errors

| Error Code | Description | Handling |
|------------|-------------|----------|
| 404 | Agent not found | Check agent name is "finops-cost-data-analyst" |
| 422 | Invalid request | Validate request schema |
| 500 | BigQuery error | Check credentials and permissions |
| 504 | Timeout | Increase timeout or simplify query |

### Error Detection

```python
def is_error_response(response_json):
    """Check if response contains an error."""
    for event in response_json:
        if event.get("type") == "agent_error":
            return True, event.get("error")
    return False, None

# Usage
response = requests.post(url, json=payload)
is_error, error_msg = is_error_response(response.json())

if is_error:
    log.error(f"Agent error: {error_msg}")
    handle_error(error_msg)
else:
    answer = extract_answer(response.json())
```

---

## Best Practices

### 1. Session Management
- ✅ **Create new session** for each user/topic
- ✅ **Reuse session** for follow-up questions
- ✅ **Delete session** when conversation ends

```python
# Good: New session per conversation
session_id = f"budget-analysis-{uuid.uuid4()}"

# Bad: Reusing same session for unrelated queries
session_id = "global-session"  # ❌ Don't do this
```

### 2. Error Handling
- ✅ **Always check for errors** before parsing
- ✅ **Implement retries** with exponential backoff
- ✅ **Log all requests** for debugging

```python
def query_with_retry(question, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = finops_client.query(question, ...)
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### 3. Performance
- ✅ **Use parallel requests** for independent queries
- ✅ **Set appropriate timeouts** (60-120s)
- ✅ **Cache responses** when applicable

```python
# Good: Parallel independent queries
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(query, q) for q in questions]
    results = [f.result() for f in futures]

# Bad: Sequential queries when they could be parallel
for q in questions:
    result = query(q)  # ❌ Slow
```

### 4. Security
- ✅ **Use authentication** in production
- ✅ **Validate inputs** before sending
- ✅ **Don't log sensitive data**

---

## Versioning

Current version: **1.0.0**

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (e.g., schema changes)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Compatibility Promise

- **Breaking changes**: Announced 90 days before release
- **Deprecations**: Supported for 2 major versions
- **Bug fixes**: No compatibility guarantees

---

## Testing Your Integration

### Step 1: Validate Request Against Schema
```bash
# Install jsonschema
pip install jsonschema

# Validate your request
python3 << EOF
import json
from jsonschema import validate

with open('agent-card.json') as f:
    agent_card = json.load(f)

request_schema = agent_card['agentCard']['requestSchema']

your_request = {
    "appName": "finops-cost-data-analyst",
    "userId": "test-agent",
    "sessionId": "test-session",
    "newMessage": {
        "role": "user",
        "parts": [{"text": "What is the total cost?"}]
    }
}

validate(instance=your_request, schema=request_schema)
print("✅ Request is valid!")
EOF
```

### Step 2: Test with Example Queries
```bash
# Test with examples from agent card
cat agent-card.json | jq '.agentCard.examples[] | .request' > test-requests.json
```

### Step 3: Run Integration Tests
```bash
# Use provided test script
cd examples/
./api_test.sh
```

---

## Support

- **Documentation**: `docs/API_GUIDE.md`
- **Examples**: `examples/api_client.py`
- **Issues**: Report via GitHub issues
- **Contact**: finops-team@company.com

---

## Summary

✅ **Agent Card** (`agent-card.json`) - Complete agent specification
✅ **A2A Spec** (`a2a-spec.json`) - Communication templates & examples
✅ **Schemas** - JSON schemas for validation
✅ **Examples** - Real-world use cases
✅ **Integration Code** - Python, JavaScript, curl examples

**Next Steps:**
1. Read agent card to understand capabilities
2. Choose appropriate intent for your use case
3. Use request template from A2A spec
4. Test with examples
5. Integrate with your agent

---

**Version**: 1.0.0 | **Last Updated**: 2025-10-24
