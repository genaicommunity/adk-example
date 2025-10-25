# Production Deployment Guide

**Ready to deploy FinOps Cost Data Analyst to your production environment**

---

## 📋 Pre-Deployment Checklist

### ✅ What You Need Before Copying

- [ ] Google Cloud Project ID (your production project)
- [ ] BigQuery dataset and table names (your actual data)
- [ ] Google Cloud service account with BigQuery permissions
- [ ] Service account JSON key file
- [ ] Gemini API key (from https://aistudio.google.com/app/apikey)

---

## 🎯 Configuration Files to Update

### 1. `.env` File (REQUIRED)

**Location**: `finops-cost-data-analyst/.env`

**Create from template**:
```bash
cp .env.example .env
```

**Update these values**:

```bash
# =============================================================================
# STEP 1: Google GenAI API Key
# =============================================================================
GOOGLE_API_KEY=your-actual-api-key-here

# =============================================================================
# STEP 2: Google Cloud Service Account
# =============================================================================
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-production-service-account.json
GOOGLE_CLOUD_PROJECT=your-production-project-id
GOOGLE_CLOUD_LOCATION=us-central1  # Or your region

# =============================================================================
# STEP 3: BigQuery Configuration
# =============================================================================
# Replace with YOUR actual BigQuery project ID
BIGQUERY_PROJECT=your-production-project-id

# Optional fallback hints (if you have different naming)
BIGQUERY_DATASET=your_cost_dataset_name
BIGQUERY_TABLE=your_cost_table_name

# =============================================================================
# STEP 4: Model Configuration (optional - defaults work fine)
# =============================================================================
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
SQL_GENERATOR_MODEL=gemini-2.0-flash-exp
```

### 2. Service Account Permissions

**Required IAM roles** for the service account:

```
roles/bigquery.dataViewer
roles/bigquery.jobUser
```

**Specific permissions needed**:
- `bigquery.datasets.get`
- `bigquery.tables.get`
- `bigquery.tables.list`
- `bigquery.jobs.create`

**Grant permissions**:
```bash
# Replace with your service account email
SERVICE_ACCOUNT="your-sa@your-project.iam.gserviceaccount.com"
PROJECT="your-production-project-id"

gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/bigquery.jobUser"
```

---

## 📊 BigQuery Schema Setup

### Your Production Data Structure

The agent expects BigQuery tables with this structure:

#### Cost Analysis Table (Primary)

**Your naming** (examples - use your actual names):
- Dataset: `production_costs`, `cost_data`, `finance_costs`
- Table: `cost_analysis`, `cloud_costs`, `spending_data`

**Required columns**:
```sql
CREATE TABLE `your-project.your_dataset.your_table` (
  date DATE NOT NULL,
  cto STRING,                    -- Optional: CTO/department
  cloud STRING,                  -- Cloud provider (GCP, AWS, Azure)
  application STRING,            -- Application name
  managed_service STRING,        -- Service type
  environment STRING,            -- prod, dev, staging
  cost FLOAT64                   -- Cost amount
)
PARTITION BY DATE(date)
CLUSTER BY application, cloud;
```

**✅ The agent will automatically find your tables** if they contain these columns!

#### Optional: Budget Table

```sql
CREATE TABLE `your-project.budget_dataset.budget` (
  date DATE NOT NULL,
  application STRING,
  budget_amount FLOAT64,
  fiscal_year STRING,
  department STRING
)
PARTITION BY DATE(date);
```

#### Optional: Usage Table

```sql
CREATE TABLE `your-project.usage_dataset.usage` (
  date DATE NOT NULL,
  resource_type STRING,
  application STRING,
  usage_hours FLOAT64,
  usage_amount FLOAT64
)
PARTITION BY DATE(date);
```

---

## 🚀 Deployment Steps

### Step 1: Copy Project to Production Server

```bash
# From your local machine
rsync -av --exclude='.git' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='.env' \
          finops-cost-data-analyst/ \
          production-server:/path/to/deployment/
```

**Or using git**:
```bash
# On production server
git clone <your-repo-url>
cd finops-cost-data-analyst
```

### Step 2: Create Production `.env` File

```bash
cd finops-cost-data-analyst
cp .env.example .env
nano .env  # Edit with your production values
```

**Update**:
- `GOOGLE_API_KEY` → Your Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS` → Path to service account JSON
- `GOOGLE_CLOUD_PROJECT` → Your production project ID
- `BIGQUERY_PROJECT` → Your production project ID
- `BIGQUERY_DATASET` → Your cost dataset name (optional)
- `BIGQUERY_TABLE` → Your cost table name (optional)

### Step 3: Copy Service Account Key

```bash
# Copy service account JSON to server
scp your-service-account.json production-server:/path/to/keys/

# Update .env to point to it
GOOGLE_APPLICATION_CREDENTIALS=/path/to/keys/your-service-account.json
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install google-adk requests jsonschema
```

### Step 5: Test Configuration

```bash
# Test authentication
gcloud auth application-default login  # Or use service account

# Test BigQuery access
bq ls --project_id=your-production-project-id

# Test agent import
python3 -c "from agent import root_agent; print(f'✓ Agent loaded: {root_agent.name}')"
```

### Step 6: Start ADK Web Server

```bash
# From parent directory
cd /path/to/deployment
adk web --port 8000

# Or with specific host
adk web --host 0.0.0.0 --port 8000
```

### Step 7: Verify Deployment

```bash
# Test API endpoint
curl http://localhost:8000/list-apps

# Expected response:
# ["finops-cost-data-analyst"]

# Test session creation
curl -X POST http://localhost:8000/apps/finops-cost-data-analyst/users/test/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🔒 Security Best Practices

### 1. Protect `.env` File

```bash
# Set restrictive permissions
chmod 600 .env

# Never commit to git
echo ".env" >> .gitignore
```

### 2. Protect Service Account Key

```bash
# Store in secure location
mkdir -p /opt/secure/keys
chmod 700 /opt/secure/keys
mv your-service-account.json /opt/secure/keys/
chmod 600 /opt/secure/keys/your-service-account.json
```

### 3. Network Security

```bash
# Use firewall to restrict access
# Allow only from authorized IPs

# Use HTTPS in production
# Set up reverse proxy (nginx/Apache) with SSL
```

### 4. API Key Rotation

```bash
# Rotate Gemini API key regularly
# Update .env and restart service
```

---

## 🔧 What to Customize (Safe to Change)

### ✅ These are SAFE to customize for your company:

1. **BigQuery Configuration** (`.env`):
   ```bash
   BIGQUERY_PROJECT=your-company-project-id
   BIGQUERY_DATASET=your-dataset-name
   BIGQUERY_TABLE=your-table-name
   ```

2. **Fiscal Year Definitions** (`prompts.py` lines 10-30):
   ```python
   # Update if your fiscal year is different
   FY26 = "February 1, 2025 to January 31, 2026"
   ```

3. **Agent Display Name** (`agent-card.json`):
   ```json
   "displayName": "Your Company FinOps Agent"
   ```

4. **Example Queries** (`agent-card.json`):
   - Update example project names
   - Update example application names
   - Update cloud provider names

---

## ❌ What NOT to Change (Keep Logic Intact)

### 🚫 DO NOT modify:

1. **Agent Architecture** (`agent.py`, `sub_agents.py`):
   - SequentialAgent structure
   - Sub-agent order
   - output_key parameters
   - Tool assignments

2. **SQL Generation Logic** (`prompts.py`):
   - Multi-table discovery workflow
   - Validation rules
   - Security checks

3. **Tool Definitions** (`_tools/`):
   - BigQuery toolsets
   - Validation functions
   - Security validators

4. **Request/Response Schemas** (`agent-card.json`):
   - JSON Schema definitions
   - Required fields
   - Type definitions

---

## 📝 Example Production `.env`

```bash
# =============================================================================
# ACME Corp Production - FinOps Cost Data Analyst
# =============================================================================

# Google GenAI API
GOOGLE_API_KEY=AIzaSyABC123xyz789...

# Google Cloud (ACME Corp Production)
GOOGLE_APPLICATION_CREDENTIALS=/opt/secure/keys/acme-finops-sa.json
GOOGLE_CLOUD_PROJECT=acme-production-12345
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery (ACME Corp Data Warehouse)
BIGQUERY_PROJECT=acme-production-12345
BIGQUERY_DATASET=finance_costs          # Your actual dataset
BIGQUERY_TABLE=cloud_spending          # Your actual table

# Model Configuration
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
SQL_GENERATOR_MODEL=gemini-2.0-flash-exp

# Logging
LOG_LEVEL=INFO
```

---

## 🧪 Testing After Deployment

### 1. Test Agent Discovery

```bash
# List available agents
curl http://localhost:8000/list-apps

# Should return: ["finops-cost-data-analyst"]
```

### 2. Test Session Creation

```bash
# Create session
curl -X POST http://localhost:8000/apps/finops-cost-data-analyst/users/prod-test/sessions \
  -H "Content-Type: application/json" \
  -d '{}'

# Save session ID from response
```

### 3. Test Query Execution

```bash
# Run test query
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "prod-test",
    "sessionId": "YOUR-SESSION-ID",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for FY26?"}]
    }
  }'
```

### 4. Test Multi-Table Discovery

```bash
# Query should automatically discover your tables
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "prod-test",
    "sessionId": "YOUR-SESSION-ID",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What are the top 10 applications by cost?"}]
    }
  }'
```

---

## 🔍 Troubleshooting

### Issue: "Session not found"

**Cause**: Session wasn't created before querying

**Fix**: Always create session first:
```bash
curl -X POST http://localhost:8000/apps/.../sessions -d '{}'
```

### Issue: "BigQuery permission denied"

**Cause**: Service account lacks permissions

**Fix**: Grant required roles:
```bash
gcloud projects add-iam-policy-binding YOUR-PROJECT \
    --member="serviceAccount:YOUR-SA@..." \
    --role="roles/bigquery.dataViewer"
```

### Issue: "Table not found"

**Cause**: Wrong dataset/table name in `.env`

**Fix**: Update `.env` with correct names:
```bash
BIGQUERY_DATASET=your_actual_dataset
BIGQUERY_TABLE=your_actual_table
```

### Issue: "API quota exceeded"

**Cause**: Too many requests to Gemini API

**Fix**:
- Wait for quota reset (10 requests/minute default)
- Upgrade to higher quota tier
- Add rate limiting in client code

---

## 📊 Monitoring Production

### Check Server Status

```bash
# Check if server is running
ps aux | grep "adk web"

# Check port is listening
netstat -an | grep 8000
```

### View Logs

```bash
# ADK web server logs
tail -f /tmp/adk_web.log

# Or if using systemd
journalctl -u adk-web -f
```

### Monitor API Usage

```bash
# Check Gemini API usage
# Visit: https://aistudio.google.com/app/apikey

# Check BigQuery usage
bq ls -j --max_results=10 --project_id=YOUR-PROJECT
```

---

## 🚀 Production Deployment Options

### Option 1: Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY finops-cost-data-analyst/ /app/
COPY .env /app/.env
COPY service-account.json /opt/keys/

RUN pip install google-adk requests jsonschema

ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/keys/service-account.json

EXPOSE 8000

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 2: Systemd Service

```ini
[Unit]
Description=FinOps Cost Data Analyst
After=network.target

[Service]
Type=simple
User=finops
WorkingDirectory=/opt/finops-agent
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/local/bin/adk web --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 3: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finops-agent
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: agent
        image: finops-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /secrets/service-account.json
        volumeMounts:
        - name: secrets
          mountPath: /secrets
      volumes:
      - name: secrets
        secret:
          secretName: finops-sa-key
```

---

## 📋 Deployment Checklist

Before going live:

- [ ] Updated `.env` with production values
- [ ] Copied service account key to secure location
- [ ] Granted BigQuery permissions to service account
- [ ] Tested authentication with production project
- [ ] Verified table schemas match expected structure
- [ ] Tested session creation
- [ ] Tested query execution
- [ ] Tested multi-table discovery
- [ ] Set up monitoring/logging
- [ ] Configured firewall rules
- [ ] Set up HTTPS/SSL
- [ ] Documented production configuration
- [ ] Created backup of configuration

---

## 📞 Support

If you encounter issues:

1. Check logs: `tail -f /tmp/adk_web.log`
2. Verify configuration: `cat .env`
3. Test BigQuery access: `bq ls`
4. Review documentation: `docs/`

---

## 🎯 Summary

### Files to Update:
1. `.env` → Your production configuration
2. Service account JSON → Your production credentials

### What Changes Automatically:
- Agent discovers YOUR BigQuery tables
- Agent adapts to YOUR schema
- Agent uses YOUR project ID

### What Stays the Same:
- All logic and algorithms
- Agent architecture
- Security validation
- Multi-agent workflow

**Your data + Same logic = Production ready!** 🚀

---

**Last Updated**: 2025-10-24
**Version**: 1.0.0
**Status**: Production Ready ✅
