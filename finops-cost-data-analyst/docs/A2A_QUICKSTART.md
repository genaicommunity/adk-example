# Agent-to-Agent (A2A) Communication - Quick Start

**Enable API access for the FinOps Cost Data Analyst agent without any code changes**

---

## Overview

The FinOps Cost Data Analyst agent is **already API-enabled** when you run `adk web`. No configuration changes needed!

✅ **What you get automatically:**
- REST API endpoints
- JSON request/response
- Session management
- Multi-user support
- Streaming responses (SSE)

❌ **What you DON'T need to change:**
- Agent code (agent.py, sub_agents.py, prompts.py)
- Configuration files
- Tool definitions

---

## Quick Start (3 Steps)

### Step 1: Start the Server

```bash
cd /Users/gurukallam/projects/google-adk-agents
adk web --port 8000

# Server available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Step 2: Test with curl

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "test-user",
    "sessionId": "session-123",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for FY26?"}]
    }
  }' | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text'
```

### Step 3: Test with Python

```python
import requests

payload = {
    "appName": "finops-cost-data-analyst",
    "userId": "python-client",
    "sessionId": "session-456",
    "newMessage": {
        "role": "user",
        "parts": [{"text": "What are the top 5 applications by cost?"}]
    }
}

response = requests.post("http://localhost:8000/run", json=payload)
events = response.json()

# Extract answer
for event in events:
    if event.get("type") == "agent_output":
        answer = event["content"]["parts"][0]["text"]
        print(answer)
```

---

## API Endpoints (No Code Changes Needed)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/list-apps` | GET | List available agents |
| `/run` | POST | Query agent (sync) |
| `/run_sse` | POST | Query agent (streaming) |
| `/apps/{app}/users/{user}/sessions` | GET | List sessions |
| `/docs` | GET | API documentation |

**Full API docs**: See `docs/API_GUIDE.md`

---

## Example Use Cases

### Use Case 1: Budget Agent Queries Cost Agent

```python
# Budget Agent needs actual costs from FinOps Agent
class BudgetAgent:
    def __init__(self):
        self.finops_api = "http://localhost:8000/run"

    def check_variance(self):
        # Query FinOps Agent for actual costs
        response = requests.post(self.finops_api, json={
            "appName": "finops-cost-data-analyst",
            "userId": "budget-agent",
            "sessionId": "budget-session-1",
            "newMessage": {
                "role": "user",
                "parts": [{"text": "What is the total cost for FY26?"}]
            }
        })

        # Process response and compare with budget
        actual_cost = self._extract_cost(response.json())
        budget = self.get_budget()
        variance = budget - actual_cost

        return {"actual": actual_cost, "budget": budget, "variance": variance}
```

### Use Case 2: Monitoring System Queries Agent

```bash
#!/bin/bash
# Daily cost monitoring cron job

DAILY_COST=$(curl -s -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "monitoring-system",
    "sessionId": "monitoring-'$(date +%Y%m%d)'",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for yesterday?"}]
    }
  }' | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text')

# Send to monitoring system
echo "$DAILY_COST" | ./send_to_slack.sh
```

### Use Case 3: Dashboard Backend API

```python
from fastapi import FastAPI
import requests

app = FastAPI()

FINOPS_AGENT = "http://localhost:8000/run"

@app.get("/api/costs/total")
def get_total_cost():
    """Dashboard endpoint that queries FinOps agent."""
    response = requests.post(FINOPS_AGENT, json={
        "appName": "finops-cost-data-analyst",
        "userId": "dashboard",
        "sessionId": f"dashboard-{datetime.now().date()}",
        "newMessage": {
            "role": "user",
            "parts": [{"text": "What is the total cost for FY26?"}]
        }
    })

    # Extract and return
    for event in response.json():
        if event.get("type") == "agent_output":
            return {"answer": event["content"]["parts"][0]["text"]}

    return {"error": "No response"}
```

---

## Testing Tools

### 1. Shell Script (Comprehensive Tests)

```bash
cd /Users/gurukallam/projects/google-adk-agents/finops-cost-data-analyst
./examples/api_test.sh
```

**What it tests:**
- Server connectivity
- Simple queries
- Top applications
- Cloud provider breakdown
- Multi-turn conversations

### 2. Python Client (Full Examples)

```bash
cd /Users/gurukallam/projects/google-adk-agents/finops-cost-data-analyst
python3 examples/api_client.py
```

**What it demonstrates:**
- Simple queries
- Conversation with context
- Agent-to-agent communication pattern
- Error handling

### 3. Swagger UI (Interactive API Testing)

Open browser: http://localhost:8000/docs

- Interactive API documentation
- Try endpoints directly in browser
- See request/response schemas
- No code required

---

## Production Deployment

### Option 1: Expose via Port Forwarding (Quick)

```bash
# Run on server
adk web --port 8000 --host 0.0.0.0

# Access from other machines
curl http://your-server-ip:8000/run -X POST ...
```

⚠️ **Security Warning**: No authentication! Use only in trusted networks.

### Option 2: Behind Reverse Proxy (Recommended)

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name finops-api.company.com;

    # Add authentication here
    auth_basic "FinOps API";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

### Option 3: Cloud Run (GCP)

```bash
# Deploy to Cloud Run with authentication
gcloud run deploy finops-agent \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated

# Get service URL
SERVICE_URL=$(gcloud run services describe finops-agent --format='value(status.url)')

# Call with authentication
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  $SERVICE_URL/run -X POST ...
```

---

## Security Checklist

For production A2A communication:

- [ ] **Authentication**: Add API keys or OAuth 2.0
- [ ] **Rate Limiting**: Prevent abuse (e.g., 100 req/min per user)
- [ ] **HTTPS**: Use TLS encryption
- [ ] **Network Security**: Use VPN or private network
- [ ] **Logging**: Log all API requests for audit
- [ ] **Input Validation**: Validate all inputs (ADK does basic validation)
- [ ] **Monitoring**: Track API usage, errors, latency

**See `docs/API_GUIDE.md` for detailed security recommendations.**

---

## Troubleshooting

### "Connection refused"
```bash
# Check if server is running
curl http://localhost:8000/list-apps

# If not running, start it
adk web --port 8000
```

### "Agent not found"
```bash
# List available agents
curl http://localhost:8000/list-apps

# Use exact agent name from response
# Must be: "finops-cost-data-analyst"
```

### "BigQuery permission denied"
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-authenticate
gcloud auth application-default login
```

### Timeout errors
```python
# Increase timeout for complex queries
response = requests.post(url, json=payload, timeout=120)  # 2 minutes
```

---

## Advanced Topics

### Streaming Responses (Server-Sent Events)

```python
import requests

response = requests.post(
    "http://localhost:8000/run_sse",
    json={
        "appName": "finops-cost-data-analyst",
        "userId": "streaming-user",
        "sessionId": "stream-1",
        "newMessage": {
            "role": "user",
            "parts": [{"text": "What are the top 10 applications?"}]
        },
        "streaming": True
    },
    stream=True,
    headers={"Accept": "text/event-stream"}
)

for line in response.iter_lines():
    if line:
        data = line.decode('utf-8')
        if data.startswith("data: "):
            event = json.loads(data[6:])
            print(f"Event: {event.get('type')}")
```

### Session Management

```python
# Create session
session_resp = requests.post(
    "http://localhost:8000/apps/finops-cost-data-analyst/users/user-123/sessions",
    json={}
)
session_id = session_resp.json()["session_id"]

# Use session for multiple queries
for question in questions:
    response = requests.post(url, json={
        "appName": "finops-cost-data-analyst",
        "userId": "user-123",
        "sessionId": session_id,  # Same session = maintains context
        "newMessage": {"role": "user", "parts": [{"text": question}]}
    })

# Delete session when done
requests.delete(
    f"http://localhost:8000/apps/finops-cost-data-analyst/users/user-123/sessions/{session_id}"
)
```

---

## Summary

✅ **Enabled out-of-the-box** - No code changes required
✅ **REST API** - Standard HTTP/JSON interface
✅ **Multiple languages** - Use curl, Python, Node.js, Go, etc.
✅ **Production-ready** - Add auth, rate limiting, monitoring
✅ **Documented** - Swagger UI + comprehensive guides

**Next Steps:**
1. Start server: `adk web --port 8000`
2. Run tests: `./examples/api_test.sh`
3. Integrate: Use Python client or curl examples
4. Production: Add authentication and deploy

**Full Documentation:**
- API Guide: `docs/API_GUIDE.md`
- Python Examples: `examples/api_client.py`
- Shell Tests: `examples/api_test.sh`
- Swagger UI: http://localhost:8000/docs
