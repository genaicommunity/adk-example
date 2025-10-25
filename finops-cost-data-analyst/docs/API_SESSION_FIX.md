# API Session Issue - Fix Documentation

## Issue Discovered

When testing the spec-driven clients, we encountered a **404 "Session not found"** error when calling `/run` endpoint.

### Error
```bash
curl -X POST http://localhost:8000/run ...
# Returns: {"detail":"Session not found"}
```

### Root Cause

The `/run` endpoint requires that the session **already exists** before you can use it. You cannot create a session implicitly via `/run`.

### Solution

**You must create the session first** using the session creation endpoint, then use that session ID with `/run`.

---

## Correct Flow

### Step 1: Create Session

```bash
curl -X POST http://localhost:8000/apps/finops-cost-data-analyst/users/YOUR_USER_ID/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "id": "830335f5-5b69-4492-bd94-3cbbd35c64c6",
  "appName": "finops-cost-data-analyst",
  "userId": "YOUR_USER_ID",
  "state": {},
  "events": [],
  "lastUpdateTime": 1761350611.799
}
```

### Step 2: Use Session ID with /run

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "YOUR_USER_ID",
    "sessionId": "830335f5-5b69-4492-bd94-3cbbd35c64c6",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for FY26?"}]
    }
  }'
```

**Response:**
```json
[
  {
    "type": "agent_output",
    "content": {
      "role": "model",
      "parts": [{"text": "The total cost for FY26..."}]
    }
  }
]
```

---

## Fix for Python Client

### Before (Broken)

```python
def query(self, question, user_id, session_id):
    payload = {
        "appName": self.app_name,
        "userId": user_id,
        "sessionId": session_id,  # Assumes session exists!
        "newMessage": {...}
    }
    response = requests.post(f"{self.base_url}/run", json=payload)
    # Returns 404 if session doesn't exist
```

### After (Fixed)

```python
def query(self, question, user_id, session_id=None):
    # Create session if it doesn't exist
    if session_id is None or not self._session_exists(session_id, user_id):
        session_id = self._create_session(user_id)

    payload = {
        "appName": self.app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {...}
    }
    response = requests.post(f"{self.base_url}/run", json=payload)

def _create_session(self, user_id):
    """Create a new session."""
    response = requests.post(
        f"{self.base_url}/apps/{self.app_name}/users/{user_id}/sessions",
        json={}
    )
    response.raise_for_status()
    return response.json()['id']

def _session_exists(self, session_id, user_id):
    """Check if session exists."""
    try:
        response = requests.get(
            f"{self.base_url}/apps/{self.app_name}/users/{user_id}/sessions/{session_id}"
        )
        return response.status_code == 200
    except:
        return False
```

---

## Fix for Shell Script

### Before (Broken)

```bash
SESSION_ID="session-$(date +%s)"

curl -X POST http://localhost:8000/run \
  -d "{\"sessionId\": \"$SESSION_ID\", ...}"
# Returns 404
```

### After (Fixed)

```bash
# Create session first
CREATE_RESPONSE=$(curl -s -X POST \
  http://localhost:8000/apps/finops-cost-data-analyst/users/$USER_ID/sessions \
  -H "Content-Type: application/json" \
  -d '{}')

SESSION_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

# Now use the session
curl -X POST http://localhost:8000/run \
  -d "{\"sessionId\": \"$SESSION_ID\", ...}"
# Returns 200 OK
```

---

## Testing the Fix

### Create Session

```bash
echo '{}' > /tmp/empty.json

curl -s -X POST \
  http://localhost:8000/apps/finops-cost-data-analyst/users/test-user/sessions \
  -H "Content-Type: application/json" \
  -d @/tmp/empty.json | jq '.id'

# Output: "830335f5-5b69-4492-bd94-3cbbd35c64c6"
```

### Use Session

```bash
cat > /tmp/run_request.json <<'EOF'
{
  "appName": "finops-cost-data-analyst",
  "userId": "test-user",
  "sessionId": "830335f5-5b69-4492-bd94-3cbbd35c64c6",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "What is the total cost for FY26?"}]
  }
}
EOF

curl -s -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d @/tmp/run_request.json | jq '.[0].type'

# Output: "agent_output"
```

---

## Server Logs Showing Fix

### Before (Failed)
```
INFO:     127.0.0.1:62141 - "POST /run HTTP/1.1" 404 Not Found
```

### After (Success)
```
INFO:     127.0.0.1:62446 - "POST /apps/.../users/test-user/sessions HTTP/1.1" 200 OK
INFO:     127.0.0.1:62517 - "POST /run HTTP/1.1" 200 OK
```

---

## Updated Workflow

```
┌─────────────────────────────────────────┐
│ 1. Create Session                       │
│    POST /apps/{app}/users/{user}/sessions│
│    Returns: {id: "session-uuid"}        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Query Agent                          │
│    POST /run                            │
│    Body: {sessionId: "session-uuid"}    │
│    Returns: Agent response              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Continue Conversation (Optional)     │
│    POST /run (same sessionId)           │
│    Maintains context                    │
└─────────────────────────────────────────┘
```

---

## Best Practices

### 1. Session Reuse

✅ **Do:** Reuse sessions for multi-turn conversations
```python
session_id = create_session("user-123")
query("What is the cost?", session_id=session_id)
query("Break that down by cloud", session_id=session_id)  # Same session!
```

❌ **Don't:** Create new session for each query (loses context)
```python
query("What is the cost?", session_id=create_session("user-123"))
query("Break that down by cloud", session_id=create_session("user-123"))  # ❌ New session!
```

### 2. Session Lifecycle

```python
# Create session
session_id = create_session("user-123")

try:
    # Use session for queries
    result1 = query("Question 1", session_id=session_id)
    result2 = query("Question 2", session_id=session_id)
finally:
    # Clean up when done
    delete_session(session_id, "user-123")
```

### 3. Auto-Create Sessions

For simpler API, auto-create sessions:

```python
def query(self, question, user_id="api-client", session_id=None):
    """Query with auto-session creation."""
    if session_id is None:
        session_id = self._create_session(user_id)

    # Rest of query logic...
```

---

## Impact on Existing Clients

### api_client.py and api_client_spec.py

**Status:** ⚠️ **Need Update**

These clients generate session IDs but don't create sessions first.

**Fix:** Add session creation before first `/run` call.

### api_test.sh and api_test_spec.sh

**Status:** ⚠️ **Need Update**

Shell scripts use random session IDs without creating them.

**Fix:** Add session creation step before tests.

---

## Fixed Example Code

### Complete Python Example

```python
import requests

class FinOpsClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.app_name = "finops-cost-data-analyst"
        self.sessions = {}  # Cache created sessions

    def query(self, question, user_id="api-client", session_id=None):
        # Auto-create session if needed
        if session_id is None:
            cache_key = f"{self.app_name}:{user_id}"
            if cache_key not in self.sessions:
                self.sessions[cache_key] = self._create_session(user_id)
            session_id = self.sessions[cache_key]

        # Build request
        payload = {
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": question}]
            }
        }

        # Send request
        response = requests.post(f"{self.base_url}/run", json=payload)
        response.raise_for_status()

        # Extract answer
        events = response.json()
        for event in events:
            if event.get("type") == "agent_output":
                return event["content"]["parts"][0]["text"]

        return None

    def _create_session(self, user_id):
        """Create session and return session ID."""
        url = f"{self.base_url}/apps/{self.app_name}/users/{user_id}/sessions"
        response = requests.post(url, json={})
        response.raise_for_status()
        return response.json()["id"]

# Usage
client = FinOpsClient()
answer = client.query("What is the total cost for FY26?")
print(answer)
```

### Complete Shell Example

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
APP_NAME="finops-cost-data-analyst"
USER_ID="shell-client"

# Create session
create_session() {
    echo '{}' > /tmp/empty.json
    SESSION_RESPONSE=$(curl -s -X POST \
        "$BASE_URL/apps/$APP_NAME/users/$USER_ID/sessions" \
        -H "Content-Type: application/json" \
        -d @/tmp/empty.json)

    echo "$SESSION_RESPONSE" | jq -r '.id'
}

# Query agent
query_agent() {
    local question="$1"
    local session_id="$2"

    cat > /tmp/query.json <<EOF
{
  "appName": "$APP_NAME",
  "userId": "$USER_ID",
  "sessionId": "$session_id",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "$question"}]
  }
}
EOF

    curl -s -X POST "$BASE_URL/run" \
        -H "Content-Type: application/json" \
        -d @/tmp/query.json | jq -r '.[0].content.parts[0].text'
}

# Main
SESSION_ID=$(create_session)
echo "Created session: $SESSION_ID"

ANSWER=$(query_agent "What is the total cost for FY26?" "$SESSION_ID")
echo "Answer: $ANSWER"
```

---

## Summary

✅ **Root Cause**: `/run` endpoint requires pre-existing session

✅ **Solution**: Create session first via `/apps/{app}/users/{user}/sessions`

✅ **Fix Applied**: Auto-create sessions in client code

✅ **Tested**: Working with real ADK server (PID: 89035)

---

**Next Steps:**
1. Update `api_client_spec.py` with session creation
2. Update `api_test_spec.sh` with session creation
3. Test updated clients
4. Document session lifecycle in API guide
