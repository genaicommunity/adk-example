# FinOps Cost Data Analyst - Developer Guide

## Mandatory Configuration

### Environment Variables (.env)
```bash
# ============================================================================
# REQUIRED: Multi-Table Discovery
# ============================================================================
BIGQUERY_PROJECT=gac-prod-471220          # Your GCP project ID

# ============================================================================
# OPTIONAL: Fallback hints (if dynamic discovery fails)
# ============================================================================
BIGQUERY_DATASET=agent_bq_dataset          # Fallback cost dataset name
BIGQUERY_TABLE=cost_analysis               # Fallback cost table name

# ============================================================================
# Multi-Table FinOps Setup (Recommended Naming for Auto-Discovery)
# ============================================================================
# The agent uses pattern matching to discover these datasets/tables:
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
# ============================================================================

# OPTIONAL: Model Configuration
ROOT_AGENT_MODEL=gemini-2.0-flash-exp      # Model for all agents
```

### Google Cloud Setup
1. **Authentication**: `gcloud auth application-default login`
2. **IAM Permissions** (minimum for multi-table discovery):
   - `roles/bigquery.dataViewer` (read datasets, tables, data)
   - `roles/bigquery.jobUser` (create and run queries)
   - Specific permissions:
     - `bigquery.datasets.get` (list and describe datasets)
     - `bigquery.tables.get` (get table schema)
     - `bigquery.tables.list` (list tables in dataset)
     - `bigquery.jobs.create` (execute queries)

3. **BigQuery Table Schemas** (3 Datasets):

**Dataset 1: Cost Analysis (Actual Spending)**
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

**Dataset 2: Budget (Allocations & Forecasts)**
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

**Dataset 3: Resource Usage (Utilization Metrics)**
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

## Architecture Flow

### SequentialAgent Pattern (CORRECT - CURRENT IMPLEMENTATION)

```
agent.py (Root File - NOT in subfolder)
  ├─ Root Agent: SequentialAgent
  │   ├─ name: "FinOpsCostAnalystOrchestrator"
  │   ├─ description: ROOT_AGENT_DESCRIPTION
  │   └─ sub_agents: [...]  ← NOT tools!
  │
  └─ Sub-Agents (all defined in agent.py, sequential execution):
      1. sql_generation (LlmAgent) ⚡ DYNAMIC MULTI-TABLE DISCOVERY
         - Tools: [bigquery_schema_toolset]
           • list_dataset_ids (lists all datasets in project - NEW!)
           • list_table_ids (lists all tables in dataset)
           • get_table_info (fetches schema from BigQuery)
           • get_dataset_info (dataset metadata)
         - output_key: "sql_query"
         - Workflow (5 Steps):
           a) Classify query intent (COST/BUDGET/USAGE/COMPARISON)
           b) Call list_dataset_ids() to discover all datasets
           c) Match dataset to query type using pattern matching
           d) Call list_table_ids() to discover tables in dataset
           e) Call get_table_info() to get schema
           f) Generate SQL using discovered schema
         - Writes: state['sql_query']

      2. sql_validation (LlmAgent)
         - Tools: [validation_tools]
           • check_forbidden_keywords
           • parse_sql_query
           • validate_sql_security
         - output_key: "validation_result"
         - Reads: state['sql_query']
         - Writes: state['validation_result']

      3. query_execution (LlmAgent)
         - Tools: [bigquery_execution_toolset]
           • execute_sql (read-only query execution)
         - output_key: "query_results"
         - Reads: state['sql_query']
         - Writes: state['query_results']

      4. insight_synthesis (LlmAgent)
         - NO tools (formatting only)
         - output_key: "final_insights"
         - Reads: state['sql_query'], state['query_results']
         - Writes: state['final_insights']
```

### Anti-Pattern (WRONG - DO NOT USE)
```python
# ❌ WRONG: Root as LlmAgent with wrapper tools
root_agent = LlmAgent(
    tools=[call_sql_generation_agent, call_sql_validation_agent, ...]  # NO!
)

# ❌ WRONG: Absolute imports (breaks ADK package loading)
from prompts import ROOT_AGENT_DESCRIPTION
from _tools import bigquery_toolset

# ❌ WRONG: Nested agents/ directory
finops-cost-data-analyst/
  └── agents/              # ❌ ADK won't find agent.py here
      └── agent.py
```

### Correct Pattern (CURRENT)
```python
# ✅ CORRECT: Root as SequentialAgent
root_agent = SequentialAgent(
    name="FinOpsCostAnalystOrchestrator",
    description=ROOT_AGENT_DESCRIPTION,
    sub_agents=[...]  # List of LlmAgent instances
)

# ✅ CORRECT: Relative imports (works with ADK package loading)
from .prompts import ROOT_AGENT_DESCRIPTION
from ._tools import bigquery_toolset

# ✅ CORRECT: Flat structure
finops-cost-data-analyst/
  ├── agent.py           # ✅ ADK looks here
  ├── prompts.py
  └── _tools/
```

## Multi-Table Discovery Mechanism

### How Agent Discovers Datasets, Tables, and Schemas

**Answer: DYNAMIC MULTI-TABLE DISCOVERY using BigQuery ADK Toolset** ✅

When user asks: **"What is total cost for FY26?"**

### Dynamic Multi-Table Discovery Workflow (5 Steps - CURRENT)

**Step 1: Classify Query Intent**

The SQL Generation Agent analyzes the user's query:
```
User Query: "What is total cost for FY26?"
Classification: COST query
Pattern Keywords: "cost", "spending", "expenses"
Target Dataset Type: *cost*, *spending*, *expense*
```

**Step 2: Discover All Datasets in Project**

The agent makes a live API call to BigQuery:
```python
list_dataset_ids(project_id="gac-prod-471220")
```

Response:
```python
["cost_dataset", "budget_dataset", "usage_dataset"]
```

**Step 3: Match Dataset to Query Type**

Pattern matching logic:
```python
# COST queries → *cost*, *spending*, *expense*
# BUDGET queries → *budget*, *forecast*, *allocation*
# USAGE queries → *usage*, *utilization*, *resource*

# For COST query:
selected_dataset = "cost_dataset"  # Matches "*cost*" pattern
```

**Step 4: Discover Tables in Selected Dataset**

```python
list_table_ids(
    project_id="gac-prod-471220",
    dataset_id="cost_dataset"
)
```

Response:
```python
["cost_analysis", "historical_costs"]
```

Pattern matching:
```python
selected_table = "cost_analysis"  # Best match for cost queries
```

**Step 5: Get Table Schema**

```python
get_table_info(
    project_id="gac-prod-471220",
    dataset_id="cost_dataset",
    table_id="cost_analysis"
)
```

Example response:
```json
{
  "tableReference": {
    "projectId": "gac-prod-471220",
    "datasetId": "cost_dataset",
    "tableId": "cost_analysis"
  },
  "schema": {
    "fields": [
      {"name": "date", "type": "DATE", "mode": "NULLABLE"},
      {"name": "cto", "type": "STRING", "mode": "NULLABLE"},
      {"name": "cloud", "type": "STRING", "mode": "NULLABLE"},
      {"name": "application", "type": "STRING", "mode": "NULLABLE"},
      {"name": "managed_service", "type": "STRING", "mode": "NULLABLE"},
      {"name": "environment", "type": "STRING", "mode": "NULLABLE"},
      {"name": "cost", "type": "FLOAT", "mode": "NULLABLE"}
    ]
  },
  "numRows": "156234",
  "description": "FinOps cost analysis data"
}
```

**Step 6: Generate SQL Using Discovered Schema**

```sql
SELECT SUM(cost) as total_cost
FROM `gac-prod-471220.cost_dataset.cost_analysis`
WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
```

### Multi-Table JOIN Example

**Query**: "Compare FY26 budget vs actual costs"

**Discovery Process**:
1. **Classify**: COMPARISON query (needs 2 tables)
2. **Discover Datasets**: cost_dataset + budget_dataset
3. **Discover Tables**: cost_analysis + budget
4. **Get Schemas**: Both table schemas
5. **Generate JOIN**:

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

### BigQuery ADK Toolsets (3 Specialized Toolsets)

**1. bigquery_schema_toolset** (SQL Generation Agent - Multi-Table Discovery)
- `list_dataset_ids`: ⭐ **NEW!** Lists all datasets in project (multi-table support)
- `list_table_ids`: ⭐ Lists all tables in a dataset
- `get_table_info`: ⭐ Fetches table schema dynamically from BigQuery
- `get_dataset_info`: Fetches dataset metadata

**2. bigquery_execution_toolset** (Query Execution Agent)
- `execute_sql`: Executes validated SQL queries (read-only)

**3. bigquery_analytics_toolset** (Future Expansion - Phase 3)
- `execute_sql`: SQL execution
- `forecast`: BigQuery AI time series forecasting
- `ask_data_insights`: Natural language data insights

### Why Dynamic Multi-Table Discovery?

**Advantages** (CURRENT IMPLEMENTATION):
1. **Portable** - Works with ANY BigQuery project/datasets (just change .env)
2. **Self-healing** - Adapts automatically to schema changes
3. **Accurate** - Uses exact schema from source of truth
4. **Intelligent Routing** - Automatically selects correct tables (cost/budget/usage)
5. **Multi-source Analysis** - Generates JOIN queries across datasets
6. **Explorable** - Can discover new tables/datasets dynamically without code changes
7. **Future-ready** - Foundation for AI forecasting & insights

**Disadvantages**:
1. **Slightly slower** - Adds ~200-300ms for discovery API calls
2. **Requires additional permissions** - Needs `bigquery.datasets.get`, `bigquery.tables.list`

### Configuration (_tools/bigquery_tools.py)

```python
# Schema discovery toolset (Multi-Table Support)
bigquery_schema_toolset = BigQueryToolset(
    tool_filter=[
        "get_table_info",      # Dynamic schema discovery
        "get_dataset_info",    # Dataset metadata
        "list_table_ids",      # Table listing
        "list_dataset_ids",    # NEW: Dataset discovery for multi-table support
    ],
    bigquery_tool_config=BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,  # Security: no writes
    ),
)

# Query execution toolset
bigquery_execution_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],
    bigquery_tool_config=BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
    ),
)
```

### Advanced Analytics (Available but Not Enabled)

The agent has access to BigQuery AI capabilities:

**forecast** - Time series forecasting:
```sql
-- Agent could generate this automatically
SELECT * FROM ML.FORECAST(
  MODEL my_model,
  STRUCT(30 AS horizon)
)
```

**ask_data_insights** - Natural language insights:
```python
# Agent could call this directly
ask_data_insights(
    question="What are the cost trends?",
    table="gac-prod-471220.agent_bq_dataset.cost_analysis"
)
```

To enable: Change sql_generation_agent tools to `[bigquery_analytics_toolset]`

### Migration Path: Hardcoded → Dynamic

**Old (Deleted):**
```python
sql_generation_agent = LlmAgent(
    tools=[],  # No tools - schema hardcoded in prompt
)
```

**New (Current):**
```python
sql_generation_agent = LlmAgent(
    tools=[bigquery_schema_toolset],  # Dynamic schema discovery
)
```

## Data Flow Details

### State Dictionary (Shared Memory)

```python
state = {
    'sql_query': str,           # From sql_generation
    'validation_result': str,    # From sql_validation ("VALID" or "INVALID: reason")
    'query_results': dict,       # From query_execution (BigQuery results)
    'final_insights': str        # From insight_synthesis (formatted output)
}
```

### Sequential Execution Example (with Dynamic Multi-Table Discovery)

**User Query**: "What is total cost for FY26?"

1. **sql_generation** → multi-table discovery + generates SQL → `state['sql_query']`:

   **Step 1a: Classify Query**
   ```
   Classification: COST query
   Keywords: "cost"
   Target: *cost*, *spending* datasets
   ```

   **Step 1b**: Calls `list_dataset_ids("gac-prod-471220")`
   ```python
   ["cost_dataset", "budget_dataset", "usage_dataset"]
   ```

   **Step 1c**: Match dataset
   ```python
   selected_dataset = "cost_dataset"  # Matches "*cost*"
   ```

   **Step 1d**: Calls `list_table_ids("gac-prod-471220", "cost_dataset")`
   ```python
   ["cost_analysis"]
   ```

   **Step 1e**: Calls `get_table_info("gac-prod-471220", "cost_dataset", "cost_analysis")`
   ```json
   {
     "schema": {"fields": [
       {"name": "date", "type": "DATE"},
       {"name": "cost", "type": "FLOAT"},
       ...
     ]},
     "numRows": "156234"
   }
   ```

   **Step 1f**: Generates SQL using discovered schema:
   ```sql
   SELECT SUM(cost) as total_cost
   FROM `gac-prod-471220.cost_dataset.cost_analysis`
   WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
   ```

2. **sql_validation** → validates SQL → `state['validation_result']`:
   ```
   VALID
   ```

3. **query_execution** → executes SQL → `state['query_results']`:
   ```
   total_cost
   27442275.64
   ```

4. **insight_synthesis** → formats results → `state['final_insights']`:
   ```
   The total cost for FY26 (February 2025 - January 2026) was $27,442,275.64.

   This represents cloud spending across all providers and applications
   for the current fiscal year.
   ```

## File Structure (CURRENT - VERIFIED WORKING)

```
finops-cost-data-analyst/              ← Run 'adk web' from PARENT directory
├── agent.py                           ← Root SequentialAgent + all sub-agents (ADK entry point)
├── prompts.py                         ← All prompts (ROOT_AGENT_DESCRIPTION, etc.)
├── _tools/                            ← Tools package (underscore prefix hides from ADK discovery)
│   ├── __init__.py                    ← Exports all tools
│   ├── validation_tools.py            ← check_forbidden_keywords, parse_sql_query, validate_sql_security
│   └── bigquery_tools.py              ← bigquery_toolset (BigQueryToolset instance)
├── eval/
│   └── eval_data/
│       └── simple.test.json           ← Eval test cases
├── test_simple.py                     ← Structural validation test
├── .env                               ← Environment config (gitignored)
├── .env.example                       ← Example environment file
├── Readme.md                          ← User documentation
└── CLAUDE.md                          ← This file (developer guide)
```

**CRITICAL**: Do NOT create nested `agents/` or `sub_agents/` directories. All code in `agent.py` at root level.

## Running ADK Web (IMPORTANT)

### Correct Way
```bash
# From PARENT directory
cd /Users/gurukallam/projects/google-adk-agents
adk web

# Then in browser: http://localhost:8000
# Select "finops-cost-data-analyst" from dropdown
```

### Wrong Way (DO NOT DO THIS)
```bash
# ❌ From inside agent directory
cd /Users/gurukallam/projects/google-adk-agents/finops-cost-data-analyst
adk web
# This will cause "Root Agent not found" error
```

## Import Patterns (CRITICAL)

### Why Relative Imports?

When ADK runs from parent directory, it loads your agent as:
```python
import importlib
module = importlib.import_module('finops-cost-data-analyst.agent')
```

This treats `finops-cost-data-analyst/` as a **Python package**.

### Correct Imports (agent.py)
```python
# ✅ CORRECT - Relative imports
from .prompts import (
    ROOT_AGENT_DESCRIPTION,
    get_sql_generation_prompt,
    SQL_VALIDATION_PROMPT,
    get_query_execution_prompt,
    INSIGHT_SYNTHESIS_PROMPT,
)

from ._tools import (
    check_forbidden_keywords,
    parse_sql_query,
    validate_sql_security,
    bigquery_toolset,
)
```

### Wrong Imports (agent.py)
```python
# ❌ WRONG - Absolute imports fail
from prompts import ROOT_AGENT_DESCRIPTION  # ModuleNotFoundError!
from _tools import bigquery_toolset          # ModuleNotFoundError!
```

## Adding New Sub-Agents

### Template (Add to agent.py)

```python
# In agent.py (after existing sub-agents, before root_agent definition)

# ============================================================================
# SUB-AGENT 5: NEW AGENT
# ============================================================================

new_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="new_agent",
    instruction="Your instruction here...",
    output_key="new_agent_output",  # MANDATORY - writes to state['new_agent_output']
    tools=[...],  # Optional - attach tools if needed
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,  # Adjust as needed
    ),
)

# Then update root_agent sub_agents list:
root_agent = SequentialAgent(
    name="FinOpsCostAnalystOrchestrator",
    description=ROOT_AGENT_DESCRIPTION,
    sub_agents=[
        sql_generation_agent,
        sql_validation_agent,
        query_execution_agent,
        insight_synthesis_agent,
        new_agent,  # ← Add here
    ]
)
```

### Integration Steps
1. Add prompt to `prompts.py`
2. Add new sub-agent definition to `agent.py`
3. Add to `root_agent.sub_agents` list
4. If using new tools, add to `_tools/` package

## Testing Strategy

### Structure Validation
```bash
python3 test_simple.py  # Validates architecture
```

Checks:
- Root is SequentialAgent
- Sub-agents are LlmAgent
- Each has output_key
- Tools correctly attached

### Eval Framework
```bash
adk eval --eval-file eval/eval_data/simple.test.json
```

### Manual Testing
```bash
# Test import as ADK does
python3 -c "
import sys
sys.path.insert(0, '/Users/gurukallam/projects/google-adk-agents')
import importlib
module = importlib.import_module('finops-cost-data-analyst.agent')
print(f'✓ root_agent: {module.root_agent.name}')
"

# Test with .env
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from agent import root_agent
print(f'✓ {root_agent.name} with {len(root_agent.sub_agents)} sub-agents')
"
```

## Common Issues

### ❌ "Root Agent not found"
**Cause**: Running `adk web` from wrong directory
**Fix**: Run from parent directory (`google-adk-agents/`), NOT from `finops-cost-data-analyst/`

### ❌ "No module named 'prompts'"
**Cause**: Using absolute imports instead of relative
**Fix**: Change `from prompts import ...` to `from .prompts import ...`

### ❌ "No module named 'agents'"
**Cause**: ADK looking for wrong file
**Fix**: Ensure `agent.py` exists at root of `finops-cost-data-analyst/` (not in subfolder)

### ❌ BigQuery permission denied
**Fix**: Run `gcloud auth application-default login`

### ❌ "output_key not found in state"
**Fix**: Ensure previous agent has `output_key` defined

## Key Design Rules

1. **Root Agent**:
   - MUST be `SequentialAgent`
   - MUST have `sub_agents=[]`
   - MUST NOT have `tools=[]`
   - MUST use `description=` (not `instruction=`)

2. **Sub-Agents**:
   - MUST be `LlmAgent`
   - MUST have `output_key` parameter
   - CAN have `tools=[]` if needed
   - MUST use `instruction=` parameter

3. **Imports**:
   - MUST use relative imports (`from .prompts import ...`)
   - NOT absolute imports (`from prompts import ...`)

4. **File Structure**:
   - `agent.py` MUST be at root level
   - Tools in `_tools/` package (underscore prefix)
   - NO nested `agents/` directories

5. **Data Flow**:
   - MUST use `output_key` to write to state
   - MUST read from `state[...]` for sequential flow

6. **Prompts**:
   - MUST be centralized in `prompts.py`
   - MUST include schema for sql_generation
   - MUST include security rules for sql_validation

7. **Running ADK**:
   - MUST run `adk web` from parent directory
   - Agent folder name = dropdown name

## Performance Tuning

### Temperature Settings
- SQL Generation: `0.01` (deterministic)
- SQL Validation: `0.0` (strict)
- Query Execution: `0.0` (deterministic)
- Insight Synthesis: `0.1` (slight creativity for formatting)

### Model Selection
- Production: `gemini-2.0-flash-exp` (fast, cost-effective)
- Complex Queries: `gemini-pro` (more capable)
- Development: `gemini-2.0-flash-exp` (fastest iteration)

## Architecture Comparison

### Old (Deleted) vs New (Current)

**OLD (agents.py + sub_agents/ folders) - DELETED:**
```
finops-cost-data-analyst/
├── agents.py                    # Root SequentialAgent
├── sub_agents/                  # ❌ Caused import issues
│   ├── sql_generation/
│   │   └── agent.py
│   ├── sql_validation/
│   │   ├── agent.py
│   │   └── tools.py
│   └── ...
```

**NEW (agent.py flat) - CURRENT:**
```
finops-cost-data-analyst/
├── agent.py                     # ✅ Root + all sub-agents in one file
├── prompts.py                   # ✅ Centralized prompts
└── _tools/                      # ✅ Tools package (underscore prefix)
    ├── __init__.py
    ├── validation_tools.py
    └── bigquery_tools.py
```

**Why Changed?**
- Simpler imports (relative imports work cleanly)
- Easier ADK discovery (no nested packages)
- All agent definitions in one place
- Tools properly isolated in `_tools/` package

## References

- **ADK Pattern**: `adk-samples/python/agents/data-science/`
- **ADK Docs**: https://google.github.io/adk-docs/
- **Known Issues**: github.com/google/adk-python/issues/2553 (Root Agent not found bug)

---

**Architecture Verified**: ✅ SequentialAgent → LlmAgent (with tools + output_key) → State-based flow → Dynamic Multi-Table Discovery ⚡ → Intelligent Query Routing
