# FinOps Cost Data Analyst - API Guide

**Agent-to-Agent (A2A) Communication via REST API**

---

## Overview

The FinOps Cost Data Analyst agent is automatically exposed via REST API when running `adk web`. This allows:

- **Agent-to-Agent (A2A) communication** - Other agents can query this agent
- **External system integration** - Applications can integrate via HTTP
- **Programmatic access** - Scripts and automation tools can call the agent
- **Multi-user support** - Session management per user

**Base URL**: `http://localhost:8000` (configurable via `--port` flag)

**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## Quick Start

### 1. Start the ADK Web Server

```bash
# From project root
cd /Users/gurukallam/projects/google-adk-agents
adk web --port 8000

# Server will be available at http://localhost:8000
```

### 2. Make an API Call

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "appName": "finops-cost-data-analyst",
  "userId": "user-123",
  "sessionId": "session-456",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "What is the total cost for FY26?"}]
  }
}
EOF
```

---

## Core API Endpoints

### 1. **List Available Agents**

Get all agents running on this ADK server.

**Endpoint**: `GET /list-apps`

**Request**:
```bash
curl http://localhost:8000/list-apps
```

**Response**:
```json
[
  "finops-cost-data-analyst"
]
```

---

### 2. **Run Agent (Synchronous)**

Invoke the agent and get complete response when done.

**Endpoint**: `POST /run`

**Request Body**:
```json
{
  "appName": "finops-cost-data-analyst",
  "userId": "string",              // Unique user identifier
  "sessionId": "string",            // Session ID (for conversation history)
  "newMessage": {
    "role": "user",
    "parts": [{"text": "Your question here"}]
  },
  "streaming": false,               // Optional: default false
  "stateDelta": {}                  // Optional: additional state
}
```

**Response**:
```json
[
  {
    "type": "agent_output",
    "content": {
      "role": "model",
      "parts": [
        {
          "text": "The total cost for FY26 YTD (February 1, 2025 to today) is $15,234,567.89..."
        }
      ]
    },
    "metadata": {
      "session_id": "session-456",
      "event_id": "evt_abc123"
    }
  }
]
```

---

### 3. **Run Agent (Streaming SSE)**

Get real-time streaming responses using Server-Sent Events.

**Endpoint**: `POST /run_sse`

**Request Body**: Same as `/run`

**Response**: Server-Sent Events stream

**Example**:
```bash
curl -N -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "user-123",
    "sessionId": "session-456",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What are the top 5 applications by cost?"}]
    },
    "streaming": true
  }'
```

**SSE Response Format**:
```
data: {"type": "agent_start", "event_id": "evt_123"}

data: {"type": "tool_call", "tool_name": "list_dataset_ids", "status": "running"}

data: {"type": "tool_result", "tool_name": "list_dataset_ids", "result": [...]}

data: {"type": "agent_output", "content": {"parts": [{"text": "Here are..."}]}}

data: [DONE]
```

---

### 4. **Session Management**

Create, retrieve, update, or delete sessions.

**Create Session**:
```bash
POST /apps/{app_name}/users/{user_id}/sessions
```

**Get Session**:
```bash
GET /apps/{app_name}/users/{user_id}/sessions/{session_id}
```

**List Sessions**:
```bash
GET /apps/{app_name}/users/{user_id}/sessions
```

**Delete Session**:
```bash
DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}
```

---

## Python Client Examples

### Example 1: Simple Query

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
APP_NAME = "finops-cost-data-analyst"

def query_agent(question: str, user_id: str = "python-client", session_id: str = "session-1"):
    """Query the FinOps agent."""

    payload = {
        "appName": APP_NAME,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [{"text": question}]
        }
    }

    response = requests.post(f"{BASE_URL}/run", json=payload)
    response.raise_for_status()

    events = response.json()

    # Extract agent's response
    for event in events:
        if event.get("type") == "agent_output":
            content = event.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                if "text" in part:
                    return part["text"]

    return None

# Usage
if __name__ == "__main__":
    answer = query_agent("What is the total cost for FY26?")
    print(answer)
```

**Output**:
```
The total cost for FY26 YTD (February 1, 2025 to today) is $15,234,567.89.

This represents cloud spending across all providers and applications
for the current fiscal year to date.
```

---

### Example 2: Agent-to-Agent Communication

```python
import requests
from typing import Dict, Any

class FinOpsAgentClient:
    """Client for FinOps Cost Data Analyst Agent."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.app_name = "finops-cost-data-analyst"

    def query(self, question: str, user_id: str, session_id: str) -> str:
        """Send a query to the agent and get response."""
        payload = {
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": question}]
            }
        }

        response = requests.post(f"{self.base_url}/run", json=payload, timeout=60)
        response.raise_for_status()

        return self._extract_text(response.json())

    def _extract_text(self, events: list) -> str:
        """Extract text from event stream."""
        for event in events:
            if event.get("type") == "agent_output":
                parts = event.get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        return part["text"]
        return ""

# Example: Budget Agent calling FinOps Agent
class BudgetAgent:
    """Example: Another agent that queries FinOps Agent."""

    def __init__(self):
        self.finops_client = FinOpsAgentClient()

    def analyze_budget_variance(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Analyze budget variance by querying cost data from FinOps Agent."""

        # Get actual costs from FinOps Agent
        cost_query = "What is the total cost for FY26?"
        actual_cost_response = self.finops_client.query(
            question=cost_query,
            user_id=user_id,
            session_id=f"{session_id}-finops"
        )

        # Parse response and do budget analysis
        # (This is simplified - you'd parse the actual number from response)
        print(f"FinOps Agent Response: {actual_cost_response}")

        return {
            "actual_costs": actual_cost_response,
            "analysis": "Budget variance analysis based on FinOps data"
        }

# Usage
if __name__ == "__main__":
    budget_agent = BudgetAgent()
    result = budget_agent.analyze_budget_variance(
        user_id="budget-agent",
        session_id="session-789"
    )
    print(json.dumps(result, indent=2))
```

---

### Example 3: Streaming Response

```python
import requests
import json

def query_agent_streaming(question: str):
    """Query agent with streaming response."""

    payload = {
        "appName": "finops-cost-data-analyst",
        "userId": "streaming-client",
        "sessionId": "stream-session",
        "newMessage": {
            "role": "user",
            "parts": [{"text": question}]
        },
        "streaming": True
    }

    with requests.post(
        "http://localhost:8000/run_sse",
        json=payload,
        stream=True,
        headers={"Accept": "text/event-stream"}
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix

                    if data_str == "[DONE]":
                        break

                    try:
                        event = json.loads(data_str)
                        print(f"Event: {event.get('type')}")

                        if event.get('type') == 'agent_output':
                            parts = event.get('content', {}).get('parts', [])
                            for part in parts:
                                if 'text' in part:
                                    print(f"Response: {part['text']}")
                    except json.JSONDecodeError:
                        pass

# Usage
query_agent_streaming("What are the top 5 applications by cost?")
```

---

## cURL Examples

### Example 1: Total Cost Query

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "curl-user",
    "sessionId": "session-001",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for FY26?"}]
    }
  }' | jq '.[] | select(.type=="agent_output") | .content.parts[0].text'
```

### Example 2: Top Applications

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "curl-user",
    "sessionId": "session-002",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What are the top 10 applications by cost?"}]
    }
  }' | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text'
```

### Example 3: Anomaly Detection

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "curl-user",
    "sessionId": "session-003",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "Find cost anomalies in February 2025"}]
    }
  }' | jq -r '.[] | select(.type=="agent_output") | .content.parts[0].text'
```

---

## Authentication & Security

### Current Setup (Development)

**ADK Web Server (default)**: ⚠️ **NO AUTHENTICATION**

- Open to localhost only
- No API keys required
- Suitable for development

### Production Recommendations

#### 1. **Use Reverse Proxy with Authentication**

```nginx
# nginx.conf example
server {
    listen 443 ssl;
    server_name finops-api.company.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # API key authentication
    if ($http_x_api_key != "your-secret-api-key") {
        return 401;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. **Use Cloud Load Balancer (GCP)**

```bash
# Example: Deploy to Cloud Run with IAM authentication
gcloud run deploy finops-agent \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --service-account finops-agent@project.iam.gserviceaccount.com
```

**Client authentication**:
```python
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
```

#### 3. **Use VPN/Private Network**

- Deploy ADK server in private network
- Only accessible via VPN or internal network
- No public exposure

#### 4. **API Gateway (Recommended)**

Use API Gateway (Kong, Apigee, etc.) for:
- API key management
- Rate limiting
- Request/response logging
- Traffic monitoring
- OAuth 2.0 / JWT authentication

---

## Session Management

### Session ID Best Practices

**Session IDs** maintain conversation context across multiple queries.

```python
import uuid

# Create unique session per user conversation
session_id = f"session-{uuid.uuid4()}"

# Use same session_id for related queries
query_agent("What is the total cost for FY26?", session_id=session_id)
query_agent("Break that down by cloud provider", session_id=session_id)  # Uses context

# New topic = new session
new_session = f"session-{uuid.uuid4()}"
query_agent("What are the top applications?", session_id=new_session)
```

### Session Persistence

Sessions are stored in ADK's session store (in-memory by default).

**Clear session**:
```bash
DELETE /apps/finops-cost-data-analyst/users/{user_id}/sessions/{session_id}
```

**List user sessions**:
```bash
GET /apps/finops-cost-data-analyst/users/{user_id}/sessions
```

---

## Error Handling

### Common Errors

**1. Agent Not Found (404)**:
```json
{
  "detail": "Agent 'finops-cost-data-analyst' not found"
}
```
**Solution**: Check agent name in `/list-apps`

**2. Invalid Request (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "appName"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution**: Ensure all required fields present

**3. BigQuery Errors**:
```json
{
  "type": "agent_error",
  "error": "Error: No datasets found in project..."
}
```
**Solution**: Check BigQuery credentials and permissions

### Error Handling in Python

```python
def query_agent_safe(question: str, user_id: str, session_id: str) -> dict:
    """Query agent with error handling."""
    try:
        response = requests.post(
            f"{BASE_URL}/run",
            json={
                "appName": "finops-cost-data-analyst",
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": question}]
                }
            },
            timeout=60
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}

    except requests.exceptions.HTTPError as e:
        return {"status": "error", "error": f"HTTP {e.response.status_code}: {e.response.text}"}

    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Request timeout after 60s"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## Performance & Limits

### Timeouts

- **Default request timeout**: 120 seconds
- **Recommended client timeout**: 60-90 seconds
- **Long-running queries**: Use streaming (`/run_sse`)

### Rate Limiting (Production)

Implement rate limiting at API gateway or reverse proxy:

```nginx
# nginx rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /run {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

### Concurrent Requests

- ADK Web Server handles concurrent requests
- Each request gets isolated session
- State management per session prevents conflicts

---

## Production Deployment

### Option 1: Docker

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install google-adk

# Copy agent code
COPY finops-cost-data-analyst/ /app/finops-cost-data-analyst/
COPY .env /app/.env

# Expose port
EXPOSE 8000

# Run server
CMD ["adk", "web", "--port", "8000", "--host", "0.0.0.0"]
```

**Run**:
```bash
docker build -t finops-agent .
docker run -p 8000:8000 finops-agent
```

### Option 2: Cloud Run (GCP)

```bash
# Deploy to Cloud Run
gcloud run deploy finops-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BIGQUERY_PROJECT=gac-prod-471220
```

### Option 3: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finops-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finops-agent
  template:
    metadata:
      labels:
        app: finops-agent
    spec:
      containers:
      - name: agent
        image: gcr.io/project/finops-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: BIGQUERY_PROJECT
          value: "gac-prod-471220"
---
apiVersion: v1
kind: Service
metadata:
  name: finops-agent-service
spec:
  selector:
    app: finops-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Monitoring & Debugging

### Debug Endpoints

**Get Event Trace**:
```bash
GET /debug/trace/{event_id}
```

**Get Session Trace**:
```bash
GET /debug/trace/session/{session_id}
```

### Logging

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
adk web --port 8000
```

### Health Check

```bash
# Simple health check
curl http://localhost:8000/list-apps

# Returns 200 if server is healthy
```

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/list-apps` | GET | List available agents |
| `/run` | POST | Run agent (synchronous) |
| `/run_sse` | POST | Run agent (streaming SSE) |
| `/apps/{app}/users/{user}/sessions` | GET, POST | Manage sessions |
| `/apps/{app}/users/{user}/sessions/{session}` | GET, DELETE, PATCH | Session operations |
| `/debug/trace/{event_id}` | GET | Debug event trace |
| `/docs` | GET | Swagger UI documentation |
| `/openapi.json` | GET | OpenAPI specification |

---

## Next Steps

1. ✅ Start server: `adk web --port 8000`
2. ✅ Test API: `curl http://localhost:8000/list-apps`
3. ✅ Make first query using Python client example
4. ✅ Implement authentication for production
5. ✅ Deploy to production environment
6. ✅ Set up monitoring and logging

---

**For more information**:
- ADK Documentation: https://google.github.io/adk-docs/
- Swagger UI: http://localhost:8000/docs
- Agent Documentation: `finops-cost-data-analyst/README.md`
