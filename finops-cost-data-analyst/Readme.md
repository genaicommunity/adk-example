# FinOps Cost Data Analyst Agent

Enterprise-grade multi-agent AI system for cloud financial operations using Google ADK.

## Architecture Overview

```
Root Agent (SequentialAgent) - "FinOpsCostAnalystOrchestrator"
    ↓ orchestrates via sub_agents=[]
Sub-Agents (LlmAgent instances with tools + output_key)
    ├─ sql_generation     → state['sql_query']
    ├─ sql_validation     → state['validation_result'] (tools: validation functions)
    ├─ query_execution    → state['query_results'] (tools: BigQueryToolset)
    └─ insight_synthesis  → state['final_insights']
```

## How It Works: Example Query

**User asks**: "What is the total cost for FY26?"

### Step-by-Step Flow

1. **SQL Generation Agent** (agent.py:43-52)
   - Reads hardcoded schema from prompt (prompts.py:38-91)
   - Schema includes: table name, columns (date, cto, cloud, application, managed_service, environment, cost)
   - Business rules hardcoded: FY26 = Feb 1, 2025 to Jan 31, 2026
   - Generates SQL:
     ```sql
     SELECT SUM(cost) as total_cost
     FROM `gac-prod-471220.agent_bq_dataset.cost_analysis`
     WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
     ```
   - Writes to `state['sql_query']`

2. **SQL Validation Agent** (agent.py:59-72)
   - Reads `state['sql_query']`
   - Uses tools (_tools/validation_tools.py):
     - `check_forbidden_keywords()` - blocks DROP, DELETE, INSERT, etc.
     - `parse_sql_query()` - validates SQL syntax
     - `validate_sql_security()` - comprehensive security check
   - Writes "VALID" to `state['validation_result']`

3. **Query Execution Agent** (agent.py:79-88)
   - Reads `state['sql_query']`
   - Uses BigQueryToolset (_tools/bigquery_tools.py)
   - Connects to BigQuery with credentials from .env
   - Executes SQL and returns results
   - Writes to `state['query_results']`:
     ```
     total_cost
     27442275.64
     ```

4. **Insight Synthesis Agent** (agent.py:95-104)
   - Reads `state['query_results']`
   - Formats into business-friendly output
   - Writes to `state['final_insights']`:
     ```
     The total cost for FY26 (February 2025 - January 2026) was $27,442,275.64.

     This represents cloud spending across all providers and applications
     for the current fiscal year.
     ```
   - Returns final answer to user

## Schema Discovery Mechanism

**Q: How does the agent know about schema and table details?**

**A: HARDCODED in prompts.py, NOT automatic discovery**

### Schema Configuration (prompts.py:38-91)

The SQL Generation Agent prompt **hardcodes** the following:

1. **Table Information** (from .env):
   ```python
   project = os.getenv("BIGQUERY_PROJECT", "your-project-id")
   dataset = os.getenv("BIGQUERY_DATASET", "your_dataset")
   table = os.getenv("BIGQUERY_TABLE", "cost_analysis")
   full_table = f"`{project}.{dataset}.{table}`"
   ```

2. **Column Schema** (hardcoded in prompt):
   ```
   - date (DATE) - Transaction date
   - cto (STRING) - CTO organization
   - cloud (STRING) - Cloud provider (GCP, AWS, Azure)
   - application (STRING) - Application name
   - managed_service (STRING) - Service type (e.g., 'AI/ML')
   - environment (STRING) - Environment (prod, dev, staging)
   - cost (FLOAT) - Cost amount
   ```

3. **Business Logic** (hardcoded in prompt):
   ```
   FY26 = Feb 1, 2025 to Jan 31, 2026
   FY25 = Feb 1, 2024 to Jan 31, 2025
   GenAI queries → WHERE managed_service = 'AI/ML'
   ```

### Why Hardcoded?

**Pros:**
- Fast - no schema introspection overhead
- Deterministic - always generates correct SQL
- Secure - only queries known tables
- Simple - no dynamic schema discovery complexity

**Cons:**
- Schema changes require prompt updates
- Not portable to other datasets without modification

### Future Enhancement: Dynamic Schema Discovery

To make schema discovery automatic:
1. Create a new tool: `get_bigquery_schema(project, dataset, table)`
2. Add to SQL Generation Agent's tools
3. Agent calls tool before generating SQL
4. Prompt updated: "Use schema from get_bigquery_schema() result"

**Not implemented** because hardcoded schema meets current requirements.

## Prerequisites

1. **Python 3.10+**
2. **Google Cloud Project** with BigQuery enabled
3. **Google ADK**: `pip install google-adk`
4. **Authentication**: `gcloud auth application-default login`
5. **IAM Permissions** (minimum):
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`

## Environment Setup

Create `.env` file in project root:

```bash
# BigQuery Configuration (REQUIRED)
BIGQUERY_PROJECT=gac-prod-471220          # Your GCP project ID
BIGQUERY_DATASET=agent_bq_dataset          # BigQuery dataset name
BIGQUERY_TABLE=cost_analysis               # BigQuery table name

# Model Configuration (Optional)
ROOT_AGENT_MODEL=gemini-2.0-flash-exp      # Model for all agents
```

## BigQuery Table Schema

Your BigQuery table must have this schema:

```sql
CREATE TABLE `project.dataset.cost_analysis` (
  date DATE,
  cto STRING,
  cloud STRING,
  application STRING,
  managed_service STRING,
  environment STRING,
  cost FLOAT64
);
```

## Installation

```bash
# 1. Install dependencies
pip install google-adk python-dotenv

# 2. Authenticate with Google Cloud
gcloud auth application-default login

# 3. Verify installation
python3 test_simple.py
```

## Run the Agent

### Option 1: Web Interface (Recommended)

```bash
# From parent directory (google-adk-agents/)
cd /path/to/google-adk-agents
adk web
```

Then:
1. Visit http://localhost:8000
2. Select `finops-cost-data-analyst` from dropdown
3. Start chatting!

### Option 2: CLI

```bash
cd finops-cost-data-analyst
adk run --agent agent:root_agent
```

### Option 3: Programmatic

```python
import os
os.chdir('/path/to/finops-cost-data-analyst')

from agent import root_agent

# Run query
response = root_agent.run("What is total cost for FY26?")
print(response.state['final_insights'])
```

## Example Queries

```
"What is the total cost for FY26?"
"What are the top 3 most expensive applications?"
"Show me GenAI costs by cloud provider"
"Which managed services cost the most in production?"
"Compare FY25 vs FY26 spending"
```

## Project Structure (Current)

```
finops-cost-data-analyst/              ← Run 'adk web' from PARENT directory
├── agent.py                           ← Root SequentialAgent (ADK entry point)
├── prompts.py                         ← All prompts with hardcoded schema
├── _tools/                            ← Tools package (underscore hides from ADK)
│   ├── __init__.py                    ← Exports all tools
│   ├── validation_tools.py            ← SQL security validation functions
│   └── bigquery_tools.py              ← BigQueryToolset configuration
├── eval/
│   └── eval_data/
│       └── simple.test.json           ← Eval test cases
├── test_simple.py                     ← Architecture validation test
├── .env                               ← Environment configuration (gitignored)
├── .env.example                       ← Example environment file
├── Readme.md                          ← This file
└── CLAUDE.md                          ← Developer guide
```

**IMPORTANT**: ADK expects this flat structure. Don't nest `agent.py` in subdirectories.

## Data Flow Details

### State Dictionary (Shared Memory)

```python
state = {
    'sql_query': str,           # From sql_generation (agent.py:47)
    'validation_result': str,    # From sql_validation (agent.py:62)
    'query_results': dict,       # From query_execution (agent.py:82)
    'final_insights': str        # From insight_synthesis (agent.py:98)
}
```

### Sequential Execution Pattern

Each agent:
1. Reads from `state[...]` (previous agent's output)
2. Performs its specialized task
3. Writes to `state[output_key]` for next agent

**No tools on root agent** - only sub-agents have tools.

## Testing

### Structural Test
```bash
python3 test_simple.py
```

Validates:
- Root agent is SequentialAgent
- All sub-agents are LlmAgent
- Each sub-agent has `output_key`
- Tools are correctly attached

### Evaluation Framework
```bash
adk eval --eval-file eval/eval_data/simple.test.json
```

Tests end-to-end queries against expected results.

### Manual Testing
```bash
# Test import
python3 -c "from agent import root_agent; print(root_agent.name)"

# Test with .env
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from agent import root_agent
print(f'Loaded: {root_agent.name} with {len(root_agent.sub_agents)} sub-agents')
"
```

## Key Design Principles

✅ **SequentialAgent for orchestration** - Root uses `sub_agents=[]`, NOT `tools=[]`
✅ **LlmAgent for tasks** - Each sub-agent has `output_key` parameter
✅ **Relative imports** - Use `from .prompts import ...` (not `from prompts import ...`)
✅ **State-based flow** - Data flows via `state['key']` between agents
✅ **Tool isolation** - Only sub-agents have tools, never root
✅ **Security first** - SQL validation before execution
✅ **Hardcoded schema** - Fast, deterministic, secure (no dynamic discovery)

## Common Issues & Fixes

### ❌ "Root Agent not found" in adk web
**Fix**: Run `adk web` from **parent directory**, not from inside `finops-cost-data-analyst/`

```bash
# WRONG
cd finops-cost-data-analyst && adk web

# CORRECT
cd google-adk-agents && adk web
```

### ❌ "No module named 'prompts'"
**Fix**: Use **relative imports** in `agent.py`:

```python
# WRONG
from prompts import ROOT_AGENT_DESCRIPTION

# CORRECT
from .prompts import ROOT_AGENT_DESCRIPTION
```

### ❌ BigQuery permission denied
**Fix**: Re-authenticate and check IAM:

```bash
gcloud auth application-default login
gcloud projects get-iam-policy YOUR_PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:user:YOUR_EMAIL"
```

### ❌ "output_key not found in state"
**Fix**: Ensure all sub-agents have `output_key` parameter defined.

## Performance Tuning

### Temperature Settings (agent.py)
- SQL Generation: `0.01` (deterministic SQL)
- SQL Validation: `0.0` (strict security)
- Query Execution: `0.0` (deterministic)
- Insight Synthesis: `0.1` (slight creativity for formatting)

### Model Selection
- **Production**: `gemini-2.0-flash-exp` (fast, cost-effective)
- **Complex Queries**: `gemini-pro` (more capable)
- **Development**: `gemini-2.0-flash-exp` (fastest iteration)

Set via `.env`:
```bash
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
```

## References

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Sequential Agent Pattern**: github.com/google/adk-examples
- **BigQuery Setup**: https://cloud.google.com/bigquery/docs
- **ADK Python SDK**: github.com/google/adk-python

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  User Query: "What is total cost for FY26?"                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Root Agent (SequentialAgent)                                   │
│  - Name: FinOpsCostAnalystOrchestrator                          │
│  - Role: Orchestrates 4 sub-agents sequentially                 │
│  - Tools: None (orchestration only)                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ SQL Generation  │ │ SQL Validation  │ │ Query Execution │
│ (LlmAgent)      │ │ (LlmAgent)      │ │ (LlmAgent)      │
│                 │ │                 │ │                 │
│ Input:          │ │ Input:          │ │ Input:          │
│ - User query    │ │ - state['sql_   │ │ - state['sql_   │
│ - Hardcoded     │ │   query']       │ │   query']       │
│   schema        │ │                 │ │                 │
│                 │ │ Tools:          │ │ Tools:          │
│ Tools: None     │ │ - check_        │ │ - BigQueryTool  │
│                 │ │   forbidden_    │ │   set.execute_  │
│ Output:         │ │   keywords      │ │   sql           │
│ state['sql_     │ │ - parse_sql_    │ │                 │
│ query']         │ │   query         │ │ Output:         │
│                 │ │ - validate_sql_ │ │ state['query_   │
│ Example:        │ │   security      │ │ results']       │
│ SELECT SUM(cost)│ │                 │ │                 │
│ FROM table      │ │ Output:         │ │ Example:        │
│ WHERE date      │ │ state['         │ │ total_cost      │
│ BETWEEN ...     │ │ validation_     │ │ 27442275.64     │
│                 │ │ result']        │ │                 │
│                 │ │                 │ │                 │
│                 │ │ Example:        │ │                 │
│                 │ │ "VALID"         │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Insight         │
                  │ Synthesis       │
                  │ (LlmAgent)      │
                  │                 │
                  │ Input:          │
                  │ - state['query_ │
                  │   results']     │
                  │ - state['sql_   │
                  │   query']       │
                  │                 │
                  │ Tools: None     │
                  │                 │
                  │ Output:         │
                  │ state['final_   │
                  │ insights']      │
                  │                 │
                  │ Example:        │
                  │ "The total cost │
                  │ for FY26 was    │
                  │ $27,442,275.64" │
                  └────────┬────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │  User Response     │
                  └────────────────────┘
```

---

**Built with Google ADK** | Sequential Multi-Agent Workflow | Hardcoded Schema Pattern
