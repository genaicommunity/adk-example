# FinOps Cost Data Analyst - Developer Guide

## Mandatory Configuration

### Environment Variables (.env)
```bash
# REQUIRED
BIGQUERY_PROJECT=gac-prod-471220          # Your GCP project ID
BIGQUERY_DATASET=agent_bq_dataset          # BigQuery dataset name
BIGQUERY_TABLE=cost_analysis               # BigQuery table name

# OPTIONAL
ROOT_AGENT_MODEL=gemini-2.0-flash-exp      # Model for all agents
```

### Google Cloud Setup
1. **Authentication**: `gcloud auth application-default login`
2. **IAM Permissions** (minimum):
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`
3. **BigQuery Table Schema**:
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
      1. sql_generation (LlmAgent)
         - NO tools
         - output_key: "sql_query"
         - Reads: user input + hardcoded schema from prompts.py
         - Writes: state['sql_query']

      2. sql_validation (LlmAgent)
         - Tools: [check_forbidden_keywords, parse_sql_query, validate_sql_security]
         - output_key: "validation_result"
         - Reads: state['sql_query']
         - Writes: state['validation_result']

      3. query_execution (LlmAgent)
         - Tools: [BigQueryToolset]
         - output_key: "query_results"
         - Reads: state['sql_query']
         - Writes: state['query_results']

      4. insight_synthesis (LlmAgent)
         - NO tools
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

## Schema Discovery Mechanism

### How Agent Knows About Table Schema

**Answer: HARDCODED in prompts.py**

When user asks: **"What is total cost for FY26?"**

#### Step 1: SQL Generation Agent Reads Hardcoded Schema

From `prompts.py:38-91` (`get_sql_generation_prompt()` function):

```python
def get_sql_generation_prompt() -> str:
    # Table info from .env
    project = os.getenv("BIGQUERY_PROJECT", "your-project-id")
    dataset = os.getenv("BIGQUERY_DATASET", "your_dataset")
    table = os.getenv("BIGQUERY_TABLE", "cost_analysis")
    full_table = f"`{project}.{dataset}.{table}`"

    return f"""
You are a SQL Generation Specialist...

## Table Schema

**Table**: {full_table}

**Columns** (use EXACTLY these names):
- `date` (DATE) - Transaction date
- `cto` (STRING) - CTO organization
- `cloud` (STRING) - Cloud provider (GCP, AWS, Azure)
- `application` (STRING) - Application name
- `managed_service` (STRING) - Service type (e.g., 'AI/ML')
- `environment` (STRING) - Environment (prod, dev, staging)
- `cost` (FLOAT) - Cost amount

## Business Logic (ENFORCE THESE)

**FY26**: Fiscal year 2026 = Feb 1, 2025 to Jan 31, 2026:
```sql
WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
```
"""
```

**This is NOT automatic schema discovery** - it's hardcoded into the prompt.

#### Why Hardcoded?

**Advantages:**
1. **Fast** - No schema introspection API calls
2. **Deterministic** - Always generates correct SQL
3. **Secure** - Only queries known, validated tables
4. **Simple** - No complexity of dynamic schema parsing

**Disadvantages:**
1. **Manual updates** - Schema changes require prompt modification
2. **Not portable** - Tied to specific table structure

#### Future: Dynamic Schema Discovery

To implement automatic schema discovery:

```python
# _tools/schema_tools.py (NEW FILE)
from google.cloud import bigquery

def get_bigquery_schema(project: str, dataset: str, table: str) -> dict:
    """Fetch table schema dynamically from BigQuery."""
    client = bigquery.Client(project=project)
    table_ref = f"{project}.{dataset}.{table}"
    table_obj = client.get_table(table_ref)

    schema = {}
    for field in table_obj.schema:
        schema[field.name] = {
            "type": field.field_type,
            "description": field.description or ""
        }
    return schema

# Then in agent.py:
sql_generation_agent = LlmAgent(
    tools=[get_bigquery_schema],  # Add this tool
    instruction="Call get_bigquery_schema() first, then generate SQL using returned schema"
)
```

**Not implemented** because hardcoded schema is sufficient for current needs.

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

### Sequential Execution Example

**User Query**: "What is total cost for FY26?"

1. **sql_generation** → generates SQL → `state['sql_query']`:
   ```sql
   SELECT SUM(cost) as total_cost
   FROM `gac-prod-471220.agent_bq_dataset.cost_analysis`
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

**Architecture Verified**: ✅ SequentialAgent → LlmAgent (with tools + output_key) → State-based flow → Hardcoded schema
