# FinOps Cost Data Analyst Agent

Enterprise-grade multi-agent AI system for cloud financial operations using Google ADK with **multi-table dynamic discovery**.

📖 **Quick Links**:
- [MIGRATION.md](./MIGRATION.md) - ⭐ Step-by-step setup guide (start here tomorrow!)
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Enterprise deployment checklist
- [CLAUDE.md](./CLAUDE.md) - Developer guide
- [PRD_FinOps_Agent.md](./PRD_FinOps_Agent.md) - Product requirements
- [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) - Complete technical documentation

## Architecture Overview

```
Root Agent (SequentialAgent) - "FinOpsCostAnalystOrchestrator"
    ↓ orchestrates via sub_agents=[]
Sub-Agents (LlmAgent instances with tools + output_key)
    ├─ sql_generation     → state['sql_query'] (tools: BigQuery Schema Discovery)
    ├─ sql_validation     → state['validation_result'] (tools: Security validation)
    ├─ query_execution    → state['query_results'] (tools: BigQuery Execution)
    └─ insight_synthesis  → state['final_insights'] (no tools)
```

### Key Innovation: Dynamic Multi-Table Discovery ⚡

Unlike traditional SQL agents with hardcoded schemas, this agent **dynamically discovers datasets AND tables** at runtime using BigQuery's metadata API. This makes it:
- **Portable**: Works with any BigQuery project/dataset
- **Self-healing**: Adapts to schema changes automatically
- **Accurate**: Uses exact schema from source of truth
- **Intelligent**: Automatically routes queries to correct tables (cost/budget/usage)
- **Multi-source**: Generates JOIN queries across datasets for comparison analysis

## How It Works: Example Query

**User asks**: "What is the total cost for FY26?"

### Step-by-Step Flow (with Dynamic Multi-Table Discovery)

1. **SQL Generation Agent** (agent.py:45-58)
   - **Step 1a: Classify Query** - Determines user intent: COST query
   - **Step 1b: Discover Datasets** - Calls `list_dataset_ids(project)`:
     ```python
     ["cost_dataset", "budget_dataset", "usage_dataset"]
     ```
   - **Step 1c: Match Dataset** - Selects "cost_dataset" (matches "*cost*" pattern)
   - **Step 1d: Discover Tables** - Calls `list_table_ids(project, "cost_dataset")`:
     ```python
     ["cost_analysis"]
     ```
   - **Step 1e: Get Schema** - Calls `get_table_info(project, dataset, table)`:
     ```json
     {
       "schema": {"fields": [
         {"name": "date", "type": "DATE"},
         {"name": "cto", "type": "STRING"},
         {"name": "cloud", "type": "STRING"},
         {"name": "application", "type": "STRING"},
         {"name": "managed_service", "type": "STRING"},
         {"name": "environment", "type": "STRING"},
         {"name": "cost", "type": "FLOAT"}
       ]},
       "numRows": "156234"
     }
     ```
   - **Step 1f**: Uses discovered schema + business rules (FY26 = Feb 1, 2025 to Jan 31, 2026)
   - **Step 1g**: Generates SQL:
     ```sql
     SELECT SUM(cost) as total_cost
     FROM `gac-prod-471220.cost_dataset.cost_analysis`
     WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
     ```
   - **Step 1h**: Writes to `state['sql_query']`

2. **SQL Validation Agent** (agent.py:65-77)
   - Reads `state['sql_query']`
   - Uses security validation tools (_tools/validation_tools.py):
     - `check_forbidden_keywords()` - Blocks DROP, DELETE, INSERT, etc.
     - `parse_sql_query()` - Validates SQL syntax
     - `validate_sql_security()` - Comprehensive security check
   - Writes "VALID" to `state['validation_result']`

3. **Query Execution Agent** (agent.py:85-94)
   - Reads `state['sql_query']`
   - Uses BigQuery Execution Toolset (_tools/bigquery_tools.py)
   - Connects to BigQuery with credentials from .env
   - Executes SQL and returns results
   - Writes to `state['query_results']`:
     ```
     total_cost
     27442275.64
     ```

4. **Insight Synthesis Agent** (agent.py:101-110)
   - Reads `state['query_results']` and `state['sql_query']`
   - Formats into business-friendly output with exact numbers
   - Writes to `state['final_insights']`:
     ```
     The total cost for FY26 (February 2025 - January 2026) was $27,442,275.64.

     This represents cloud spending across all providers and applications
     for the current fiscal year.
     ```
   - Returns final answer to user

## Multi-Table Discovery Mechanism

**Q: How does the agent know about schemas, datasets, and tables?**

**A: DYNAMIC MULTI-TABLE DISCOVERY using BigQuery ADK Toolset** ✅

### Dynamic Discovery Workflow (5 Steps)

When you ask **"What is total cost for FY26?"**, the agent:

#### Step 1: Classify Query
```
User Intent: COST query
Pattern Matching: "cost" keyword detected
Target Data: Cost dataset
```

#### Step 2: Discover All Datasets
```python
list_dataset_ids(project_id="gac-prod-471220")
# Returns: ["cost_dataset", "budget_dataset", "usage_dataset"]
```

#### Step 3: Match Dataset to Query Type
```python
# Pattern matching logic:
# COST queries → *cost*, *spending*, *expense*
# BUDGET queries → *budget*, *forecast*, *allocation*
# USAGE queries → *usage*, *utilization*, *resource*

Selected: "cost_dataset"  # Matches "*cost*" pattern
```

#### Step 4: Discover Tables in Dataset
```python
list_table_ids(
    project_id="gac-prod-471220",
    dataset_id="cost_dataset"
)
# Returns: ["cost_analysis", "historical_costs"]

Selected: "cost_analysis"  # Best match for cost queries
```

#### Step 5: Get Table Schema
```python
get_table_info(
    project_id="gac-prod-471220",
    dataset_id="cost_dataset",
    table_id="cost_analysis"
)
```

**Response**:
```json
{
  "schema": {
    "fields": [
      {"name": "date", "type": "DATE"},
      {"name": "cto", "type": "STRING"},
      {"name": "cloud", "type": "STRING"},
      {"name": "application", "type": "STRING"},
      {"name": "managed_service", "type": "STRING"},
      {"name": "environment", "type": "STRING"},
      {"name": "cost", "type": "FLOAT"}
    ]
  },
  "numRows": "156234"
}
```

#### Step 6: Generate SQL
```sql
SELECT SUM(cost) as total_cost
FROM `gac-prod-471220.cost_dataset.cost_analysis`
WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
```

### Multi-Table JOIN Example

**Query**: "Compare FY26 budget vs actual costs"

**Discovery Process**:
1. **Classify**: COMPARISON query (needs 2 tables)
2. **Discover**: Both cost_dataset AND budget_dataset
3. **Get Schemas**: Fetch schemas for both tables
4. **Generate JOIN**:
```sql
SELECT
  c.application,
  SUM(c.cost) as actual_cost,
  SUM(b.budget_amount) as budget,
  SUM(c.cost) - SUM(b.budget_amount) as variance
FROM `gac-prod-471220.cost_dataset.cost_analysis` c
LEFT JOIN `gac-prod-471220.budget_dataset.budget` b
  ON c.application = b.application
  AND c.date = b.date
WHERE c.date BETWEEN '2025-02-01' AND '2026-01-31'
GROUP BY c.application
ORDER BY variance DESC
LIMIT 10
```

### BigQuery Toolsets (3 Specialized Toolsets)

**1. Schema Discovery Toolset** (SQL Generation Agent)
- `list_dataset_ids`: ⭐ Lists all datasets in project (NEW - multi-table support)
- `list_table_ids`: ⭐ Lists all tables in a dataset
- `get_table_info`: ⭐ Fetches table schema dynamically from BigQuery
- `get_dataset_info`: Fetches dataset metadata

**2. Execution Toolset** (Query Execution Agent)
- `execute_sql`: Executes validated SQL queries (read-only)

**3. Analytics Toolset** (Future expansion - Phase 3)
- `execute_sql`: SQL execution
- `forecast`: BigQuery AI time series forecasting
- `ask_data_insights`: Natural language data insights

### Why Dynamic Multi-Table Discovery?

**Pros** (CURRENT IMPLEMENTATION):
- ✅ **Portable** - Works with ANY BigQuery project/datasets (just change .env)
- ✅ **Self-healing** - Automatically adapts to schema changes
- ✅ **Accurate** - Uses exact schema from source of truth
- ✅ **Intelligent Routing** - Automatically selects correct tables (cost/budget/usage)
- ✅ **Multi-source Analysis** - Generates JOIN queries across datasets
- ✅ **Explorable** - Can discover new tables/datasets without code changes
- ✅ **Future-ready** - Foundation for AI forecasting & insights

**Cons**:
- Adds ~200-300ms for discovery API calls
- Requires additional IAM permissions (`bigquery.datasets.get`, `bigquery.tables.list`)

### Configuration

**Multi-Table Setup** (.env):
```bash
# REQUIRED: Your GCP Project ID
BIGQUERY_PROJECT=gac-prod-471220

# OPTIONAL: Fallback hints (if discovery fails)
BIGQUERY_DATASET=agent_bq_dataset   # Fallback cost dataset
BIGQUERY_TABLE=cost_analysis        # Fallback cost table
```

**Recommended Dataset/Table Names** (for automatic discovery):
- **Cost**: `cost_dataset.cost_analysis`
- **Budget**: `budget_dataset.budget`
- **Usage**: `usage_dataset.resource_usage`

The agent uses pattern matching to automatically discover these datasets/tables - **no hardcoding needed**!

## Prerequisites

1. **Python 3.10+**
2. **Google Cloud Project** with BigQuery enabled
3. **Google ADK**: `pip install google-adk`
4. **Authentication**: `gcloud auth application-default login`
5. **IAM Permissions** (minimum for multi-table discovery):
   - `roles/bigquery.dataViewer` (read datasets, tables, data)
   - `roles/bigquery.jobUser` (create and run queries)
   - Specific permissions needed:
     - `bigquery.datasets.get` (list and describe datasets)
     - `bigquery.tables.get` (get table schema)
     - `bigquery.tables.list` (list tables in dataset)
     - `bigquery.jobs.create` (execute queries)

## Environment Setup

Create `.env` file in project root:

```bash
# =============================================================================
# BigQuery Configuration - Multi-Table Support
# =============================================================================
# REQUIRED: Your GCP Project ID (agent discovers datasets/tables automatically)
BIGQUERY_PROJECT=gac-prod-471220

# OPTIONAL: Fallback hints (used if dynamic discovery fails)
BIGQUERY_DATASET=agent_bq_dataset    # Fallback cost dataset name
BIGQUERY_TABLE=cost_analysis         # Fallback cost table name

# =============================================================================
# Multi-Table FinOps Setup (Recommended Naming)
# =============================================================================
# The agent automatically discovers these based on pattern matching:
#
# 1. COST ANALYSIS (Actual Spending):
#    Dataset: cost_dataset, agent_bq_dataset, costs, spending
#    Table: cost_analysis, cost_data, costs
#
# 2. BUDGET (Allocations & Forecasts):
#    Dataset: budget_dataset, budgets, financial_planning
#    Table: budget, budget_allocations, forecasts
#
# 3. USAGE (Resource Utilization):
#    Dataset: usage_dataset, resource_usage, utilization
#    Table: usage, resource_usage, consumption
#
# =============================================================================

# Model Configuration (Optional)
ROOT_AGENT_MODEL=gemini-2.0-flash-exp      # Model for all agents
```

## BigQuery Table Schemas (3 Datasets)

### 1. Cost Analysis Table (Actual Spending)

```sql
CREATE TABLE `gac-prod-471220.cost_dataset.cost_analysis` (
  date DATE NOT NULL,
  cto STRING,
  cloud STRING,
  application STRING,
  managed_service STRING,
  environment STRING,
  cost FLOAT64
)
PARTITION BY DATE(date)
CLUSTER BY application, cloud;
```

### 2. Budget Table (Allocations & Forecasts)

```sql
CREATE TABLE `gac-prod-471220.budget_dataset.budget` (
  date DATE NOT NULL,
  application STRING,
  budget_amount FLOAT64,
  fiscal_year STRING,
  department STRING
)
PARTITION BY DATE(date)
CLUSTER BY application, fiscal_year;
```

### 3. Resource Usage Table (Utilization Metrics)

```sql
CREATE TABLE `gac-prod-471220.usage_dataset.resource_usage` (
  date DATE NOT NULL,
  resource_type STRING,
  application STRING,
  usage_hours FLOAT64,
  usage_amount FLOAT64
)
PARTITION BY DATE(date)
CLUSTER BY application, resource_type;
```

**Note**: Partitioning by `date` and clustering by application/cloud improves query performance by 10-100x.

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

### Cost Queries (Single Table)
```
"What is the total cost for FY26?"
"What are the top 3 most expensive applications?"
"Show me GenAI costs by cloud provider"
"Which managed services cost the most in production?"
"Compare FY25 vs FY26 spending"
```

### Budget Queries (Single Table)
```
"What is our budget for FY26?"
"Show me budget allocation by department"
"What was the budget for ML Training in Q2?"
```

### Usage Queries (Single Table)
```
"How many compute hours did we use this month?"
"Show me resource utilization by application"
"What is our total storage usage?"
```

### Comparison Queries (Multi-Table JOINs)
```
"Compare FY26 budget vs actual costs"
"Are we over budget for FY26?"
"Show me applications that exceeded their budget"
"Compare actual costs vs budget vs usage for my application"
"What is the cost per compute hour?"
```

## Project Structure (Current)

```
finops-cost-data-analyst/              ← Run 'adk web' from PARENT directory
├── agent.py                           ← Root SequentialAgent + all sub-agents (ADK entry point)
├── prompts.py                         ← All prompts with DYNAMIC schema workflow
├── _tools/                            ← Tools package (underscore hides from ADK)
│   ├── __init__.py                    ← Exports all toolsets
│   ├── validation_tools.py            ← SQL security validation functions
│   └── bigquery_tools.py              ← 3 BigQuery toolsets:
│                                          • bigquery_schema_toolset (schema discovery)
│                                          • bigquery_execution_toolset (query execution)
│                                          • bigquery_analytics_toolset (AI features)
├── eval/
│   └── eval_data/
│       └── simple.test.json           ← Eval test cases
├── test_simple.py                     ← Architecture validation test
├── .env                               ← Environment configuration (gitignored)
├── .env.example                       ← Example environment file
├── Readme.md                          ← This file (user documentation)
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
✅ **Dynamic multi-table discovery** - Automatically discovers datasets/tables at runtime
✅ **Intelligent routing** - Pattern matching to select correct table (cost/budget/usage)
✅ **Multi-source JOINs** - Generates comparison queries across datasets
✅ **Specialized toolsets** - 3 BigQuery toolsets for different purposes (schema, execution, analytics)

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

## Architecture Diagram (with Dynamic Schema Discovery)

```
┌──────────────────────────────────────────────────────────────────┐
│  User Query: "What is total cost for FY26?"                      │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Root Agent (SequentialAgent)                                    │
│  - Name: FinOpsCostAnalystOrchestrator                           │
│  - Role: Orchestrates 4 sub-agents sequentially                  │
│  - Tools: None (orchestration only)                              │
└───────────────────────────┬──────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ SQL Generation   │ │ SQL Validation   │ │ Query Execution  │
│ (LlmAgent)       │ │ (LlmAgent)       │ │ (LlmAgent)       │
│                  │ │                  │ │                  │
│ Input:           │ │ Input:           │ │ Input:           │
│ - User query     │ │ - state['sql_    │ │ - state['sql_    │
│                  │ │   query']        │ │   query']        │
│ ⚡ DYNAMIC STEP: │ │                  │ │                  │
│ 1. Calls:        │ │ Tools:           │ │ Tools:           │
│   get_table_info │ │ - check_         │ │ - execute_sql    │
│   (BigQuery API) │ │   forbidden_     │ │   (BigQuery      │
│                  │ │   keywords       │ │   Execution      │
│ 2. Receives:     │ │ - parse_sql_     │ │   Toolset)       │
│   schema.fields  │ │   query          │ │                  │
│   [date, cost,   │ │ - validate_sql_  │ │ Output:          │
│    cto, cloud,   │ │   security       │ │ state['query_    │
│    application,  │ │   (Validation    │ │ results']        │
│    ...] + types  │ │   Toolset)       │ │                  │
│                  │ │                  │ │ Example:         │
│ 3. Generates SQL │ │ Output:          │ │ total_cost       │
│    using         │ │ state['          │ │ 27442275.64      │
│    discovered    │ │ validation_      │ │                  │
│    schema        │ │ result']         │ │                  │
│                  │ │                  │ │                  │
│ Tools:           │ │ Example:         │ │                  │
│ - get_table_info │ │ "VALID"          │ │                  │
│ - get_dataset_   │ │                  │ │                  │
│   info           │ │                  │ │                  │
│ - list_table_ids │ │                  │ │                  │
│   (Schema        │ │                  │ │                  │
│   Toolset)       │ │                  │ │                  │
│                  │ │                  │ │                  │
│ Output:          │ │                  │ │                  │
│ state['sql_      │ │                  │ │                  │
│ query']          │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Insight          │
                  │ Synthesis        │
                  │ (LlmAgent)       │
                  │                  │
                  │ Input:           │
                  │ - state['query_  │
                  │   results']      │
                  │ - state['sql_    │
                  │   query']        │
                  │                  │
                  │ Tools: None      │
                  │                  │
                  │ Output:          │
                  │ state['final_    │
                  │ insights']       │
                  │                  │
                  │ Example:         │
                  │ "The total cost  │
                  │ for FY26 was     │
                  │ $27,442,275.64.  │
                  │                  │
                  │ This represents  │
                  │ cloud spending   │
                  │ across all       │
                  │ providers..."    │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │  User Response     │
                  └────────────────────┘

Legend:
⚡ = Dynamic schema discovery at runtime
📊 = BigQuery API call for metadata
🔒 = Security validation before execution
```

---

**Built with Google ADK** | Sequential Multi-Agent Workflow | Dynamic Multi-Table Discovery ⚡ | Intelligent Query Routing
