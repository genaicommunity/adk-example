# UI Project Integration - Quick Reference

**For Frontend/UI Developers**

---

## 🎯 Files You Need

### Primary: `agent-card.json`

**Location**: `finops-cost-data-analyst/agent-card.json`

This file contains everything your UI needs to know about the API:

```javascript
// What's in agent-card.json:
{
  "agentCard": {
    "metadata": {
      "name": "finops-cost-data-analyst",     // Agent ID
      "displayName": "FinOps Cost Data Analyst",  // Show in UI
      "version": "1.0.0"
    },
    "capabilities": {
      "primary": [
        "cost-aggregation",    // Total costs
        "cost-breakdown",      // By cloud/app/service
        "cost-ranking",        // Top 10 spenders
        "trend-analysis",      // Over time
        "anomaly-detection",   // Unusual spending
        "forecasting"          // Future predictions
      ]
    },
    "intents": {
      // Each intent = what the agent can do
      // Use this to build your UI dropdowns/buttons
    },
    "requestSchema": {
      // JSON Schema for requests
      // Validate before sending
    },
    "responseSchema": {
      // JSON Schema for responses
      // What to expect back
    },
    "examples": {
      // Working example requests
      // Copy these for your UI
    }
  }
}
```

### Secondary: `a2a-spec.json`

**Location**: `finops-cost-data-analyst/a2a-spec.json`

Request templates and response patterns.

---

## 📖 Documentation

### For Developers: `docs/API_GUIDE.md`

Complete API reference with:
- Endpoint URLs
- Request/response formats
- Authentication
- Error codes
- Examples

### Quick Start: `docs/A2A_QUICKSTART.md`

3-step integration guide.

---

## 🔧 Working Code Example

### JavaScript/TypeScript Example

```typescript
// Based on agent-card.json
interface FinOpsRequest {
  appName: string;        // "finops-cost-data-analyst"
  userId: string;         // Your user/app ID
  sessionId: string;      // Session UUID
  newMessage: {
    role: "user";
    parts: [{ text: string }];
  };
}

interface FinOpsResponse {
  type: "agent_output";
  content: {
    role: "model";
    parts: [{ text: string }];
  };
}

class FinOpsClient {
  private baseUrl = "http://localhost:8000";  // Or your server
  private appName = "finops-cost-data-analyst";
  private agentCard: any;  // Load from agent-card.json

  constructor() {
    // Load agent-card.json
    this.agentCard = require('./agent-card.json').agentCard;
  }

  // Get all capabilities for UI
  getCapabilities(): string[] {
    return this.agentCard.capabilities.primary;
  }

  // Get all intents for dropdown
  getIntents(): Record<string, any> {
    return this.agentCard.intents;
  }

  // Get example queries for each intent
  getExampleQueries(intent: string): string[] {
    return this.agentCard.intents[intent]?.examples || [];
  }

  // Create session (call this first)
  async createSession(userId: string): Promise<string> {
    const response = await fetch(
      `${this.baseUrl}/apps/${this.appName}/users/${userId}/sessions`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      }
    );

    const data = await response.json();
    return data.id;  // Session UUID
  }

  // Query the agent
  async query(
    question: string,
    userId: string,
    sessionId: string
  ): Promise<string> {
    const request: FinOpsRequest = {
      appName: this.appName,
      userId: userId,
      sessionId: sessionId,
      newMessage: {
        role: "user",
        parts: [{ text: question }]
      }
    };

    const response = await fetch(
      `${this.baseUrl}/run`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      }
    );

    const events: FinOpsResponse[] = await response.json();

    // Extract answer from events
    const agentOutput = events.find(e => e.type === 'agent_output');
    return agentOutput?.content.parts[0].text || "No response";
  }
}

// Usage in your UI:
const client = new FinOpsClient();

// 1. Show capabilities in UI
const capabilities = client.getCapabilities();
console.log("Agent can:", capabilities);

// 2. Build dropdown from intents
const intents = client.getIntents();
Object.keys(intents).forEach(intent => {
  console.log(intent, ":", intents[intent].description);
});

// 3. Query the agent
async function askAgent(question: string) {
  const userId = "ui-user-123";

  // Create session first
  const sessionId = await client.createSession(userId);

  // Query
  const answer = await client.query(question, userId, sessionId);

  // Display in UI
  console.log("Answer:", answer);
}

// Example: User clicks "Total Cost" button
askAgent("What is the total cost for FY26?");
```

---

## 🎨 UI Components You Can Build

### 1. Capability Selector

Use `agentCard.capabilities.primary` to build buttons/cards:

```jsx
// React example
function CapabilitySelector() {
  const capabilities = [
    { id: "cost-aggregation", label: "Total Costs", icon: "💰" },
    { id: "cost-breakdown", label: "Cost Breakdown", icon: "📊" },
    { id: "cost-ranking", label: "Top Spenders", icon: "🏆" },
    { id: "trend-analysis", label: "Trends", icon: "📈" },
    { id: "anomaly-detection", label: "Anomalies", icon: "⚠️" },
    { id: "forecasting", label: "Forecast", icon: "🔮" }
  ];

  return (
    <div className="capabilities">
      {capabilities.map(cap => (
        <button key={cap.id} onClick={() => handleCapability(cap.id)}>
          {cap.icon} {cap.label}
        </button>
      ))}
    </div>
  );
}
```

### 2. Query Examples Dropdown

Use `agentCard.intents[intent].examples`:

```jsx
function QueryExamples({ intent }) {
  const client = new FinOpsClient();
  const examples = client.getExampleQueries(intent);

  return (
    <select onChange={(e) => handleQuery(e.target.value)}>
      <option>Select a query...</option>
      {examples.map((example, i) => (
        <option key={i} value={example}>{example}</option>
      ))}
    </select>
  );
}
```

### 3. Chat Interface

```jsx
function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const client = new FinOpsClient();

  useEffect(() => {
    // Create session on mount
    client.createSession("ui-user").then(setSessionId);
  }, []);

  async function sendMessage(question) {
    // Add user message to chat
    setMessages(prev => [...prev, { role: "user", text: question }]);

    // Query agent
    const answer = await client.query(question, "ui-user", sessionId);

    // Add agent response to chat
    setMessages(prev => [...prev, { role: "agent", text: answer }]);
  }

  return (
    <div className="chat">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          {msg.text}
        </div>
      ))}
      <input onSubmit={(e) => sendMessage(e.target.value)} />
    </div>
  );
}
```

---

## 📝 What Your UI Needs to Do

### Step 1: Initialize

```javascript
// Load agent-card.json
const agentCard = require('./agent-card.json').agentCard;

// Show capabilities in UI
const capabilities = agentCard.capabilities.primary;
```

### Step 2: Create Session (Once per user session)

```javascript
POST http://localhost:8000/apps/finops-cost-data-analyst/users/YOUR_USER_ID/sessions

Request: {}
Response: { id: "session-uuid-here" }
```

Save the `session-uuid` for this user.

### Step 3: Query Agent (Multiple times with same session)

```javascript
POST http://localhost:8000/run

Request:
{
  "appName": "finops-cost-data-analyst",
  "userId": "YOUR_USER_ID",
  "sessionId": "session-uuid-from-step-2",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "What is the total cost for FY26?"}]
  }
}

Response:
[
  {
    "type": "agent_output",
    "content": {
      "role": "model",
      "parts": [{"text": "The answer here..."}]
    }
  }
]
```

Extract the text from `response[0].content.parts[0].text`.

---

## 🔐 Environment Variables

Your UI will need:

```bash
# Backend API URL
REACT_APP_FINOPS_API_URL=http://localhost:8000

# Or for production
REACT_APP_FINOPS_API_URL=https://your-production-server.com
```

---

## 🚨 Error Handling

```typescript
try {
  const answer = await client.query(question, userId, sessionId);
  // Display answer in UI
} catch (error) {
  if (error.status === 404) {
    // Session not found - create new session
    sessionId = await client.createSession(userId);
    // Retry query
  } else if (error.status === 429) {
    // Rate limited - show message to user
    showError("Too many requests. Please wait a moment.");
  } else if (error.status === 500) {
    // Server error
    showError("Service unavailable. Please try again later.");
  }
}
```

---

## 📊 Response Parsing

The agent returns natural language text. You can:

### Option 1: Display as-is (Simplest)

```jsx
<div className="answer">
  {answer}
</div>
```

### Option 2: Parse structured data

Use patterns from `a2a-spec.json`:

```javascript
// Parse dollar amounts
const costMatch = answer.match(/\$([0-9,]+(?:\.[0-9]{2})?)/);
const cost = costMatch ? parseFloat(costMatch[1].replace(',', '')) : null;

// Parse percentages
const pctMatch = answer.match(/([0-9]+(?:\.[0-9]+)?)%/);
const percentage = pctMatch ? parseFloat(pctMatch[1]) : null;

// Parse ranked lists
const lines = answer.split('\n');
const items = lines
  .filter(line => /^\d+\./.test(line))
  .map(line => {
    const match = line.match(/^\d+\.\s+(.+?):\s+\$([0-9,]+)/);
    return match ? {
      name: match[1],
      cost: parseFloat(match[2].replace(',', ''))
    } : null;
  })
  .filter(Boolean);
```

---

## 🎯 Recommended UI Flow

```
User visits page
    ↓
Initialize client (load agent-card.json)
    ↓
Create session
    ↓
Show capabilities/intents from agent-card
    ↓
User selects query or types custom question
    ↓
Send query to agent (POST /run)
    ↓
Display answer in chat/card
    ↓
User can ask follow-up questions (same session)
```

---

## 📦 Files to Copy to Your UI Project

Minimum files needed:

```
your-ui-project/
├── public/
│   └── agent-card.json          ← Copy this (API contract)
├── src/
│   ├── api/
│   │   └── finopsClient.ts      ← Create this (based on example above)
│   └── components/
│       ├── CapabilitySelector.tsx
│       ├── QueryInput.tsx
│       └── AnswerDisplay.tsx
└── .env
    └── REACT_APP_FINOPS_API_URL=http://localhost:8000
```

Optional files for reference:
- `a2a-spec.json` - Response parsing patterns
- `docs/API_GUIDE.md` - Complete API docs

---

## 🔗 Quick Links

**Essential**:
- `agent-card.json` - Your API contract
- `docs/API_GUIDE.md` - Complete reference
- `examples/api_client_spec.py` - Working Python example (translate to JS)

**Optional**:
- `a2a-spec.json` - Advanced patterns
- `docs/A2A_QUICKSTART.md` - Quick start guide

---

## 💡 Tips

1. **Load agent-card.json at build time** - It's your source of truth
2. **Create session once per user** - Reuse for multiple queries
3. **Handle errors gracefully** - Show user-friendly messages
4. **Parse responses** - Extract structured data if needed
5. **Use TypeScript** - Type safety from JSON schemas

---

## 🚀 Next Steps

1. Copy `agent-card.json` to your UI project
2. Create API client based on example above
3. Build UI components using capabilities/intents
4. Test with example queries from agent-card.json
5. Deploy!

---

**Questions?** Check `docs/API_GUIDE.md` or `examples/api_client_spec.py`
