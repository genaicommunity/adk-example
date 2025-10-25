# Copy to Production - Quick Checklist

**Use this checklist when copying the project to your company's production environment**

---

## ✅ Step 1: Copy Project Files

### Files to Copy (Everything except):

```bash
# Copy entire project EXCEPT these:
finops-cost-data-analyst/
├── ✅ agent.py                    # COPY - Main agent
├── ✅ sub_agents.py               # COPY - Sub-agents
├── ✅ prompts.py                  # COPY - Prompts
├── ✅ __init__.py                 # COPY - Package init
├── ✅ agent-card.json             # COPY - API contract
├── ✅ a2a-spec.json               # COPY - API spec
├── ✅ A2A_SPEC_README.md          # COPY - Spec docs
├── ✅ .env.example                # COPY - Environment template
├── ❌ .env                        # DO NOT COPY - Create new
├── ✅ .gitignore                  # COPY - Git ignore rules
├── ✅ _tools/                     # COPY - All tools
├── ✅ docs/                       # COPY - All documentation
├── ✅ examples/                   # COPY - API examples
├── ✅ eval/                       # COPY - Test cases
├── ✅ test_simple.py              # COPY - Structure tests
├── ✅ CLAUDE.md                   # COPY - Developer guide
├── ✅ Readme.md                   # COPY - User docs
├── ✅ PRODUCTION_DEPLOYMENT.md    # COPY - This guide
├── ✅ UI_INTEGRATION_GUIDE.md     # COPY - UI guide
├── ✅ UI_FILES_REFERENCE.txt      # COPY - UI reference
└── ❌ __pycache__/                # DO NOT COPY - Temp files
```

### Quick Copy Command

```bash
# From your development machine
rsync -av \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='.DS_Store' \
  --exclude='.env' \
  finops-cost-data-analyst/ \
  /path/to/production/location/
```

---

## ✅ Step 2: Update Configuration Files

### File: `.env` (CREATE NEW - Don't copy old one)

**Location**: `finops-cost-data-analyst/.env`

```bash
# On production server
cd finops-cost-data-analyst
cp .env.example .env
nano .env
```

**Update these 5 values**:

```bash
# 1. Your Gemini API key
GOOGLE_API_KEY=your-company-api-key-here

# 2. Path to your service account JSON
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/company-sa.json

# 3. Your company's GCP project
GOOGLE_CLOUD_PROJECT=your-company-project-id
BIGQUERY_PROJECT=your-company-project-id

# 4. Your BigQuery dataset (optional - auto-discovered)
BIGQUERY_DATASET=your_cost_dataset_name

# 5. Your BigQuery table (optional - auto-discovered)
BIGQUERY_TABLE=your_cost_table_name
```

**That's it!** Everything else auto-configures.

---

## ✅ Step 3: Update Personal Paths (Optional)

### Files with Example Paths (Safe to leave as-is or update):

These files contain example paths like `/Users/gurukallam/...`. They're in documentation only and don't affect functionality:

**Documentation files** (optional updates):
- `docs/A2A_QUICKSTART.md` (lines: example paths)
- `docs/API_GUIDE.md` (lines: example paths)
- `examples/README.md` (lines: example paths)
- `CLAUDE.md` (lines: example paths)
- `examples/api_client_spec.py` (line 546: example path in error message)
- `examples/api_test_spec.sh` (line 143: example path in error message)

**Action**:
- ✅ Leave as-is (they're examples only)
- Or replace `/Users/gurukallam/projects/google-adk-agents` with your actual path

**Find and replace** (if you want):
```bash
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" \) \
  -exec sed -i '' 's|/Users/gurukallam/projects/google-adk-agents|/your/production/path|g' {} +
```

---

## ✅ Step 4: What to Update for Your Company

### BigQuery Project ID

**Current**: `gac-prod-471220` (80 occurrences - example only)
**Action**: ✅ **NO NEED TO CHANGE IN CODE** - Just update `.env`

The example project ID `gac-prod-471220` appears in:
- Documentation (as examples)
- CLAUDE.md (as teaching examples)
- .env.example (as template)

**✅ You only need to update**: `.env` file with YOUR project ID

The agent will automatically use your project ID from `.env`!

### Optional: Update Example Names

If you want to customize documentation examples with your company's names:

**File**: `agent-card.json`
```json
{
  "metadata": {
    "displayName": "Your Company FinOps Agent"  // Update this
  },
  "intents": {
    "COST_AGGREGATION": {
      "examples": [
        "What is the total cost for FY26?",        // Keep or update
        "What is total spending for Q4 2024?"      // Add your examples
      ]
    }
  }
}
```

---

## ✅ Step 5: BigQuery Setup

### Create Your Cost Table

Your table must have these columns (names can vary slightly):

```sql
CREATE TABLE `your-project.your-dataset.your-table` (
  date DATE NOT NULL,              -- Required
  cost FLOAT64,                    -- Required
  cloud STRING,                    -- Recommended
  application STRING,              -- Recommended
  managed_service STRING,          -- Optional
  environment STRING,              -- Optional
  cto STRING                       -- Optional
)
PARTITION BY DATE(date)
CLUSTER BY application, cloud;
```

**✅ Agent automatically discovers tables with these columns!**

---

## ❌ What NOT to Change

### Keep These Unchanged (Logic & Architecture):

```
❌ agent.py                      # Agent structure
❌ sub_agents.py                 # Sub-agent definitions
❌ prompts.py                    # Prompt logic (except fiscal year)
❌ _tools/validation_tools.py    # Security validation
❌ _tools/bigquery_tools.py      # Tool configuration
```

### Why?
- These contain the core logic
- They work with ANY BigQuery project
- They auto-adapt to YOUR data
- Changing them could break functionality

---

## ✅ What's Safe to Customize

### Can Update These:

```
✅ .env                          # YOUR configuration
✅ agent-card.json               # Display name, examples
✅ prompts.py (lines 10-30)      # Fiscal year definitions
✅ Documentation (*.md)          # Update paths, examples
```

---

## 🧪 Testing Checklist

After copying to production:

```bash
# 1. Test authentication
gcloud auth application-default login

# 2. Test BigQuery access
bq ls --project_id=your-production-project

# 3. Test agent import
python3 -c "from agent import root_agent; print('✓ Loaded')"

# 4. Start server
adk web --port 8000

# 5. Test endpoints
curl http://localhost:8000/list-apps

# 6. Create session
curl -X POST http://localhost:8000/apps/finops-cost-data-analyst/users/test/sessions -d '{}'

# 7. Run query
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "finops-cost-data-analyst",
    "userId": "test",
    "sessionId": "YOUR-SESSION-ID",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the total cost for FY26?"}]
    }
  }'
```

---

## 📊 Configuration Summary

### Only These Need Your Company's Values:

| File | What to Update | Example |
|------|----------------|---------|
| `.env` | `GOOGLE_API_KEY` | Your Gemini API key |
| `.env` | `GOOGLE_APPLICATION_CREDENTIALS` | Path to your SA JSON |
| `.env` | `GOOGLE_CLOUD_PROJECT` | `your-company-prod-123` |
| `.env` | `BIGQUERY_PROJECT` | `your-company-prod-123` |
| `.env` | `BIGQUERY_DATASET` | `your_costs` (optional) |
| `.env` | `BIGQUERY_TABLE` | `cloud_spending` (optional) |

**That's literally it!** 6 lines in 1 file.

---

## 🎯 Quick Start (5 Minutes)

```bash
# 1. Copy files (1 min)
rsync -av finops-cost-data-analyst/ /production/path/

# 2. Create .env (2 min)
cd /production/path/finops-cost-data-analyst
cp .env.example .env
nano .env  # Update 6 values

# 3. Test (1 min)
python3 -c "from agent import root_agent; print('✓ Ready')"

# 4. Start (1 min)
cd /production/path
adk web --port 8000

# Done! ✅
```

---

## 📞 Quick Reference

### Files Created New for Production:
- `.env` (from .env.example)
- Service account JSON (from Google Cloud)

### Files That Auto-Adapt:
- All agent code (reads from `.env`)
- All prompts (uses config from `.env`)
- All tools (connects to YOUR BigQuery)

### Files That Never Change:
- Core logic files (`agent.py`, `sub_agents.py`, etc.)
- Architecture
- Security validation

---

## ✅ Final Checklist

Before using in production:

- [ ] Copied all files (except `.env` and `__pycache__`)
- [ ] Created new `.env` from template
- [ ] Updated 6 values in `.env`
- [ ] Copied service account JSON to server
- [ ] Granted BigQuery permissions to service account
- [ ] Tested authentication
- [ ] Tested BigQuery access
- [ ] Tested agent import
- [ ] Started ADK web server
- [ ] Tested API endpoints
- [ ] Verified queries return correct data from YOUR tables

---

## 🚀 You're Ready!

Once you complete this checklist:
- ✅ Agent uses YOUR BigQuery data
- ✅ Agent auto-discovers YOUR tables
- ✅ All logic remains intact
- ✅ Production ready!

**See `PRODUCTION_DEPLOYMENT.md` for detailed deployment guide.**

---

**Questions?** Check:
- `PRODUCTION_DEPLOYMENT.md` - Complete deployment guide
- `docs/MIGRATION.md` - Setup instructions
- `CLAUDE.md` - Developer guide
- `docs/API_GUIDE.md` - API reference
