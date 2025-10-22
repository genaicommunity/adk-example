# Migration Guide: Setting Up Multi-Table FinOps Agent

**Purpose**: Step-by-step guide for setting up the 3 BigQuery datasets and configuring the agent.
**Audience**: DevOps, Data Engineers, FinOps Team
**Time Required**: 30-60 minutes
**Date**: October 21, 2025

---

## 📋 Pre-Migration Checklist

### Prerequisites
- [ ] GCP Project created (`gac-prod-471220` or your project)
- [ ] BigQuery API enabled
- [ ] Service account created
- [ ] You have `bigquery.admin` or equivalent permissions
- [ ] `gcloud` CLI installed and authenticated
- [ ] Python 3.10+ installed
- [ ] Google ADK installed (`pip install google-adk`)

### Required Access
```bash
# Verify your access
gcloud auth list
gcloud config get-value project

# Should show: gac-prod-471220 (or your project ID)
```

---

## 🎯 Migration Steps (Do This Tomorrow)

### STEP 1: Create BigQuery Datasets (5 minutes)

#### 1.1 Create Cost Dataset

```bash
bq mk --dataset \
  --location=US \
  --description="FinOps cost analysis and tracking" \
  gac-prod-471220:cost_dataset
```

#### 1.2 Create Budget Dataset

```bash
bq mk --dataset \
  --location=US \
  --description="Budget allocations and forecasts" \
  gac-prod-471220:budget_dataset
```

#### 1.3 Create Usage Dataset

```bash
bq mk --dataset \
  --location=US \
  --description="Resource utilization and usage metrics" \
  gac-prod-471220:usage_dataset
```

**Verify**:
```bash
bq ls --project_id=gac-prod-471220

# Should show:
#  cost_dataset
#  budget_dataset
#  usage_dataset
```

---

### STEP 2: Create BigQuery Tables (10 minutes)

#### 2.1 Create Cost Analysis Table

Save this as `create_cost_table.sql`:

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
CLUSTER BY application, cloud
OPTIONS(
  description="Cloud cost analysis data with partitioning for performance",
  require_partition_filter=false
);
```

Execute:
```bash
bq query --use_legacy_sql=false < create_cost_table.sql
```

#### 2.2 Create Budget Table

Save this as `create_budget_table.sql`:

```sql
CREATE TABLE `gac-prod-471220.budget_dataset.budget` (
  date DATE NOT NULL,
  application STRING,
  budget_amount FLOAT64,
  fiscal_year STRING,
  department STRING
)
PARTITION BY DATE(date)
CLUSTER BY application, fiscal_year
OPTIONS(
  description="Budget allocations and forecasts",
  require_partition_filter=false
);
```

Execute:
```bash
bq query --use_legacy_sql=false < create_budget_table.sql
```

#### 2.3 Create Resource Usage Table

Save this as `create_usage_table.sql`:

```sql
CREATE TABLE `gac-prod-471220.usage_dataset.resource_usage` (
  date DATE NOT NULL,
  resource_type STRING,
  application STRING,
  usage_hours FLOAT64,
  usage_amount FLOAT64
)
PARTITION BY DATE(date)
CLUSTER BY application, resource_type
OPTIONS(
  description="Resource utilization metrics",
  require_partition_filter=false
);
```

Execute:
```bash
bq query --use_legacy_sql=false < create_usage_table.sql
```

**Verify All Tables**:
```bash
# Check cost table
bq show gac-prod-471220:cost_dataset.cost_analysis

# Check budget table
bq show gac-prod-471220:budget_dataset.budget

# Check usage table
bq show gac-prod-471220:usage_dataset.resource_usage
```

---

### STEP 3: Load Sample Data (10 minutes)

#### 3.1 Create Sample Cost Data

Save as `sample_cost_data.csv`:

```csv
date,cto,cloud,application,managed_service,environment,cost
2025-02-01,Engineering,GCP,ML Training,Compute Engine,Production,15000.50
2025-02-01,Engineering,AWS,Data Pipeline,EC2,Production,8500.25
2025-02-01,Engineering,Azure,Web Frontend,App Service,Production,3200.75
2025-02-02,Engineering,GCP,ML Training,Compute Engine,Production,15200.00
2025-02-02,Engineering,AWS,Data Pipeline,EC2,Production,8450.00
```

Load:
```bash
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  gac-prod-471220:cost_dataset.cost_analysis \
  sample_cost_data.csv \
  date:DATE,cto:STRING,cloud:STRING,application:STRING,managed_service:STRING,environment:STRING,cost:FLOAT
```

#### 3.2 Create Sample Budget Data

Save as `sample_budget_data.csv`:

```csv
date,application,budget_amount,fiscal_year,department
2025-02-01,ML Training,500000,FY26,Engineering
2025-02-01,Data Pipeline,300000,FY26,Engineering
2025-02-01,Web Frontend,150000,FY26,Engineering
2025-03-01,ML Training,500000,FY26,Engineering
2025-03-01,Data Pipeline,300000,FY26,Engineering
```

Load:
```bash
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  gac-prod-471220:budget_dataset.budget \
  sample_budget_data.csv \
  date:DATE,application:STRING,budget_amount:FLOAT,fiscal_year:STRING,department:STRING
```

#### 3.3 Create Sample Usage Data

Save as `sample_usage_data.csv`:

```csv
date,resource_type,application,usage_hours,usage_amount
2025-02-01,Compute,ML Training,1200.5,15000.50
2025-02-01,Compute,Data Pipeline,850.25,8500.25
2025-02-01,Compute,Web Frontend,320.75,3200.75
2025-02-02,Compute,ML Training,1220.0,15200.00
2025-02-02,Compute,Data Pipeline,845.0,8450.00
```

Load:
```bash
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  gac-prod-471220:usage_dataset.resource_usage \
  sample_usage_data.csv \
  date:DATE,resource_type:STRING,application:STRING,usage_hours:FLOAT,usage_amount:FLOAT
```

**Verify Data Loaded**:
```bash
# Check row counts
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `gac-prod-471220.cost_dataset.cost_analysis`'
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `gac-prod-471220.budget_dataset.budget`'
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `gac-prod-471220.usage_dataset.resource_usage`'
```

---

### STEP 4: Configure IAM Permissions (5 minutes)

#### 4.1 Create Service Account (if not exists)

```bash
gcloud iam service-accounts create finops-agent \
  --display-name="FinOps Cost Data Analyst Agent" \
  --description="Service account for FinOps agent to access BigQuery"
```

#### 4.2 Grant Permissions

```bash
# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding gac-prod-471220 \
  --member="serviceAccount:finops-agent@gac-prod-471220.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User role
gcloud projects add-iam-policy-binding gac-prod-471220 \
  --member="serviceAccount:finops-agent@gac-prod-471220.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

#### 4.3 Create Service Account Key

```bash
gcloud iam service-accounts keys create ~/finops-agent-key.json \
  --iam-account=finops-agent@gac-prod-471220.iam.gserviceaccount.com

# Move to safe location
mv ~/finops-agent-key.json /path/to/secure/location/
chmod 600 /path/to/secure/location/finops-agent-key.json
```

**⚠️ SECURITY**: Never commit this file to git! It's already in `.gitignore`.

**Verify Permissions**:
```bash
gcloud projects get-iam-policy gac-prod-471220 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:finops-agent@gac-prod-471220.iam.gserviceaccount.com"
```

---

### STEP 5: Update Agent Configuration (3 minutes)

#### 5.1 Update .env File

**Location**: `finops-cost-data-analyst/.env`

**What to Update**:

```bash
# =============================================================================
# UPDATE THESE VALUES FOR YOUR ENVIRONMENT
# =============================================================================

# REQUIRED: Google Gemini API Key (for agent LLM calls)
GOOGLE_API_KEY=your-google-api-key-here

# REQUIRED: Service Account for BigQuery Access
GOOGLE_APPLICATION_CREDENTIALS=/path/to/finops-agent-key.json

# REQUIRED: GCP Project for general Google Cloud services
GOOGLE_CLOUD_PROJECT=gac-prod-471220

# REQUIRED: BigQuery Project ID (usually same as GOOGLE_CLOUD_PROJECT)
BIGQUERY_PROJECT=gac-prod-471220

# OPTIONAL: GCP Region
GOOGLE_CLOUD_LOCATION=us-central1

# OPTIONAL: Fallback hints (if dynamic discovery fails)
BIGQUERY_DATASET=agent_bq_dataset  # Fallback cost dataset
BIGQUERY_TABLE=cost_analysis       # Fallback cost table

# OPTIONAL: Model configuration
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
SQL_GENERATOR_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.01

# OPTIONAL: Logging
LOG_LEVEL=INFO

# OPTIONAL: MCP Toolbox (if using)
MCP_TOOLBOX_PATH=toolbox
```

**Complete Example .env file**:
```bash
# Google GenAI API Configuration
GOOGLE_API_KEY=AIzaSyB_your_actual_key_here

# Google Cloud Configuration (for BigQuery via service account)
GOOGLE_APPLICATION_CREDENTIALS=/Users/yourname/.gcp/finops-agent-key.json
GOOGLE_CLOUD_PROJECT=gac-prod-471220
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery Configuration (Multi-Table Discovery)
BIGQUERY_PROJECT=gac-prod-471220          # Project where datasets exist
BIGQUERY_DATASET=agent_bq_dataset          # Fallback cost dataset
BIGQUERY_TABLE=cost_analysis               # Fallback cost table

# Model Configuration
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
SQL_GENERATOR_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.01

# Logging
LOG_LEVEL=INFO

# MCP Toolbox (if using)
MCP_TOOLBOX_PATH=toolbox
```

**Important Notes**:
1. **GOOGLE_API_KEY**: Get from https://aistudio.google.com/app/apikey
2. **GOOGLE_APPLICATION_CREDENTIALS**: Path to service account key (created in Step 4)
3. **GOOGLE_CLOUD_PROJECT**: Your main GCP project ID
4. **BIGQUERY_PROJECT**: Project where BigQuery datasets exist (usually same as GOOGLE_CLOUD_PROJECT)
5. All paths should be absolute (full path from root)

#### 5.2 Verify Configuration

```bash
# Test that environment loads correctly
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(f'✓ Project: {os.getenv(\"BIGQUERY_PROJECT\")}')
print(f'✓ Credentials: {os.getenv(\"GOOGLE_APPLICATION_CREDENTIALS\")}')
"
```

---

### STEP 6: Test Agent (5 minutes)

#### 6.1 Test Import

```bash
cd /path/to/google-adk-agents/finops-cost-data-analyst

python3 -c "
from agent import root_agent
print(f'✓ Agent loaded: {root_agent.name}')
print(f'✓ Sub-agents: {len(root_agent.sub_agents)}')
"
```

Expected output:
```
✓ Agent loaded: FinOpsCostAnalystOrchestrator
✓ Sub-agents: 4
```

#### 6.2 Run Structure Test

```bash
python3 test_simple.py
```

Expected output:
```
Testing agent structure...
✓ Root agent exists
✓ Root agent is SequentialAgent
✓ Has 4 sub-agents
✓ All sub-agents are LlmAgent
✓ All sub-agents have output_key
✓ SQL Generation agent has schema toolset (4 tools)
✓ SQL Validation agent has validation tools
✓ Query Execution agent has BigQuery execution toolset
✓ Insight Synthesis agent has no tools

All tests passed! ✓
```

#### 6.3 Start ADK Web (from parent directory)

```bash
cd /path/to/google-adk-agents
adk web --port 8000
```

Then visit: http://localhost:8000

Select `finops-cost-data-analyst` from dropdown.

#### 6.4 Test Queries

Try these queries in the web UI:

**Test 1: Cost Query (Single Table)**
```
What is the total cost for February 2025?
```

Expected: Should discover `cost_dataset.cost_analysis` and return sum of costs.

**Test 2: Budget Query (Single Table)**
```
What is the budget for ML Training?
```

Expected: Should discover `budget_dataset.budget` and return budget amount.

**Test 3: Usage Query (Single Table)**
```
How many compute hours did we use in February 2025?
```

Expected: Should discover `usage_dataset.resource_usage` and return total hours.

**Test 4: Comparison Query (Multi-Table JOIN)**
```
Compare budget vs actual costs for all applications in February 2025
```

Expected: Should discover both `cost_dataset` and `budget_dataset`, generate a JOIN query, and show variance.

---

## 📂 Files You Need to Update

### Files to ALWAYS Update (When Changing Project/Datasets)

#### 1. `.env` (YOUR LOCAL CONFIG - NOT IN GIT)
**Location**: `finops-cost-data-analyst/.env`

**What to Update**:
```bash
BIGQUERY_PROJECT=gac-prod-471220              # ← UPDATE: Your project ID
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key   # ← UPDATE: Path to service account key
```

**When to Update**: Tomorrow when you create datasets, or when deploying to new environment.

---

### Files to NEVER Update (Agent Auto-Discovers)

#### 2. `agent.py` - NO CHANGES NEEDED ✅
**Why**: Agent uses dynamic discovery - works with any dataset/table names

#### 3. `prompts.py` - NO CHANGES NEEDED ✅
**Why**: Contains pattern matching logic that works with any naming convention

#### 4. `_tools/bigquery_tools.py` - NO CHANGES NEEDED ✅
**Why**: Toolsets are generic and work with any BigQuery project

---

### Optional: Update If Renaming Datasets

If you use different dataset/table names than recommended, **NO CODE CHANGES NEEDED** - the agent will still discover them via pattern matching.

But if discovery fails, you can add fallback hints to `.env`:
```bash
# OPTIONAL: Fallback hints if dynamic discovery fails
BIGQUERY_DATASET=your_custom_cost_dataset_name
BIGQUERY_TABLE=your_custom_cost_table_name
```

---

## 🔍 Verification Checklist

After completing steps 1-6, verify:

### BigQuery
- [ ] 3 datasets exist: `cost_dataset`, `budget_dataset`, `usage_dataset`
- [ ] 3 tables exist with correct schemas
- [ ] All tables have data (at least sample data)
- [ ] All tables are partitioned by `date`
- [ ] All tables are clustered correctly

### IAM
- [ ] Service account created: `finops-agent@gac-prod-471220.iam.gserviceaccount.com`
- [ ] Service account has `bigquery.dataViewer` role
- [ ] Service account has `bigquery.jobUser` role
- [ ] Service account key downloaded and secured

### Agent Configuration
- [ ] `.env` file exists in `finops-cost-data-analyst/`
- [ ] `BIGQUERY_PROJECT` set correctly
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` points to valid key file
- [ ] Agent imports successfully (`from agent import root_agent`)
- [ ] Test script passes (`python3 test_simple.py`)

### Agent Functionality
- [ ] ADK web starts successfully
- [ ] Agent appears in dropdown
- [ ] Cost queries work (single table)
- [ ] Budget queries work (single table)
- [ ] Usage queries work (single table)
- [ ] Comparison queries work (multi-table JOIN)
- [ ] Agent discovers datasets dynamically
- [ ] SQL generation uses correct table names
- [ ] Results are accurate

---

## 🚨 Troubleshooting

### Issue 1: "Access Denied" when listing datasets

**Error**:
```
ERROR: Access Denied: Project gac-prod-471220: User does not have permission to query the project
```

**Fix**:
```bash
# Re-authenticate
gcloud auth application-default login

# Verify permissions
gcloud projects get-iam-policy gac-prod-471220 --flatten="bindings[].members" --filter="bindings.members:user:YOUR_EMAIL"
```

---

### Issue 2: Agent can't find datasets

**Error** (in agent output):
```
ERROR: No datasets found in project gac-prod-471220
```

**Fix**:
```bash
# Verify datasets exist
bq ls --project_id=gac-prod-471220

# Check .env file
cat .env | grep BIGQUERY_PROJECT

# Verify credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
ls -la $GOOGLE_APPLICATION_CREDENTIALS
```

---

### Issue 3: Pattern matching fails (wrong table selected)

**Symptom**: Agent selects wrong table for query type

**Fix Option 1** (Rename datasets to recommended names):
- Cost: `cost_dataset`, `agent_bq_dataset`, `costs`, `spending`
- Budget: `budget_dataset`, `budgets`, `financial_planning`
- Usage: `usage_dataset`, `resource_usage`, `utilization`

**Fix Option 2** (Add fallback hints to `.env`):
```bash
BIGQUERY_DATASET=your_actual_cost_dataset
BIGQUERY_TABLE=your_actual_cost_table
```

---

### Issue 4: Service account key not found

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/finops-agent-key.json'
```

**Fix**:
```bash
# Verify key exists
ls -la /path/to/finops-agent-key.json

# Update .env with correct path
echo "GOOGLE_APPLICATION_CREDENTIALS=/correct/path/to/finops-agent-key.json" >> .env
```

---

### Issue 5: Tables have wrong schema

**Symptom**: Queries fail with "Column not found"

**Fix**:
```bash
# Check actual schema
bq show --schema --format=prettyjson gac-prod-471220:cost_dataset.cost_analysis

# Compare with expected schema in TECHNICAL_ARCHITECTURE.md

# If different, either:
# Option 1: Recreate table with correct schema (if empty)
bq rm -f -t gac-prod-471220:cost_dataset.cost_analysis
# Then re-run CREATE TABLE from STEP 2

# Option 2: Alter table (if has data)
bq query --use_legacy_sql=false '
ALTER TABLE `gac-prod-471220.cost_dataset.cost_analysis`
ADD COLUMN new_column STRING
'
```

---

## 📊 Data Loading Examples

### Production Data Loading

#### Option 1: Load from GCS

```bash
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --replace \
  gac-prod-471220:cost_dataset.cost_analysis \
  gs://your-bucket/cost-data/*.csv \
  date:DATE,cto:STRING,cloud:STRING,application:STRING,managed_service:STRING,environment:STRING,cost:FLOAT
```

#### Option 2: Load from SQL Query (Data Migration)

```bash
bq query --use_legacy_sql=false --destination_table=gac-prod-471220:cost_dataset.cost_analysis '
SELECT
  PARSE_DATE("%Y%m%d", date_string) as date,
  cto,
  cloud_provider as cloud,
  app_name as application,
  service as managed_service,
  env as environment,
  CAST(cost_amount as FLOAT64) as cost
FROM `old-project.old_dataset.old_cost_table`
WHERE date_string >= "20250201"
'
```

#### Option 3: Schedule Automated Loads (Data Transfer Service)

See: https://cloud.google.com/bigquery-transfer/docs/cloud-storage-transfer

---

## 🎯 Post-Migration Tasks

### Day 1 (After Setup)
- [ ] Run 10 test queries
- [ ] Verify all query types work (COST, BUDGET, USAGE, COMPARISON)
- [ ] Check query performance (< 5 seconds)
- [ ] Review generated SQL for correctness

### Week 1
- [ ] Onboard FinOps team (5 users)
- [ ] Collect user feedback
- [ ] Monitor error rates
- [ ] Tune prompts if needed

### Week 2
- [ ] Onboard finance team
- [ ] Add more historical data
- [ ] Set up monitoring dashboards
- [ ] Document common queries

### Month 1
- [ ] Evaluate for production deployment
- [ ] Set up CI/CD pipeline
- [ ] Configure Cloud Run deployment
- [ ] Implement usage tracking

---

## 📚 Related Documentation

- **README.md** - User guide and quick start
- **CLAUDE.md** - Developer guide and architecture
- **PRD_FinOps_Agent.md** - Product requirements and use cases
- **TECHNICAL_ARCHITECTURE.md** - Complete technical specs
- **.env.example** - Configuration template

---

## 🆘 Support

### For Setup Issues
- Check BigQuery: https://console.cloud.google.com/bigquery?project=gac-prod-471220
- Check IAM: https://console.cloud.google.com/iam-admin/iam?project=gac-prod-471220
- Check Service Accounts: https://console.cloud.google.com/iam-admin/serviceaccounts?project=gac-prod-471220

### For Agent Issues
- Review logs: Check terminal output when running agent
- Test structure: `python3 test_simple.py`
- Test import: `python3 -c "from agent import root_agent"`

### Documentation
- Google ADK Docs: https://google.github.io/adk-docs/
- BigQuery Docs: https://cloud.google.com/bigquery/docs
- Python ADK: https://github.com/google/adk-python

---

**Migration Prepared By**: Claude Code
**Last Updated**: October 21, 2025
**Version**: 1.0 - Multi-Table Discovery

**Status**: ✅ Ready for Tomorrow's Migration
