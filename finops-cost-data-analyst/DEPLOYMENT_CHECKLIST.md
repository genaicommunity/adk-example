# Deployment Checklist - FinOps Cost Data Analyst Agent

**Purpose**: Enterprise deployment readiness checklist
**Version**: 2.0 - Multi-Table Discovery
**Date**: October 21, 2025

---

## 📋 Pre-Deployment Checklist

### Development Environment ✅

- [x] **Code Complete**
  - [x] Multi-table discovery implemented
  - [x] 3 specialized BigQuery toolsets configured
  - [x] Security validation in place
  - [x] Dynamic schema discovery working
  - [x] Intelligent query routing implemented

- [x] **Documentation Complete**
  - [x] README.md - User guide
  - [x] CLAUDE.md - Developer guide
  - [x] PRD_FinOps_Agent.md - Product requirements
  - [x] TECHNICAL_ARCHITECTURE.md - Technical specs
  - [x] MIGRATION.md - Setup guide
  - [x] DEPLOYMENT_CHECKLIST.md - This document
  - [x] .env.example - Configuration template

- [x] **Testing Framework**
  - [x] test_simple.py - Structure validation
  - [x] eval/eval_data/simple.test.json - Integration tests
  - [x] Manual test queries documented

---

## 🔧 Infrastructure Setup

### BigQuery Resources

#### Datasets
- [ ] **cost_dataset** created in `gac-prod-471220`
  - [ ] Location: US (or your region)
  - [ ] Description added
  - [ ] Default table expiration: None (or as needed)

- [ ] **budget_dataset** created in `gac-prod-471220`
  - [ ] Location: US (matches cost_dataset)
  - [ ] Description added
  - [ ] Default table expiration: None

- [ ] **usage_dataset** created in `gac-prod-471220`
  - [ ] Location: US (matches cost_dataset)
  - [ ] Description added
  - [ ] Default table expiration: None

#### Tables
- [ ] **cost_dataset.cost_analysis**
  - [ ] Schema matches specification
  - [ ] Partitioned by DATE(date)
  - [ ] Clustered by application, cloud
  - [ ] Sample data loaded (for testing)
  - [ ] Production data loaded (for production)

- [ ] **budget_dataset.budget**
  - [ ] Schema matches specification
  - [ ] Partitioned by DATE(date)
  - [ ] Clustered by application, fiscal_year
  - [ ] Sample data loaded

- [ ] **usage_dataset.resource_usage**
  - [ ] Schema matches specification
  - [ ] Partitioned by DATE(date)
  - [ ] Clustered by application, resource_type
  - [ ] Sample data loaded

#### Data Validation
- [ ] All tables have data (row count > 0)
- [ ] Date ranges are correct (FY26 data: 2025-02-01 to 2026-01-31)
- [ ] No NULL values in critical columns (date, cost, budget_amount)
- [ ] Data types match schema (dates are DATE, costs are FLOAT64)
- [ ] Sample queries return expected results

---

## 🔐 Security & IAM

### Service Account
- [ ] Service account created: `finops-agent@gac-prod-471220.iam.gserviceaccount.com`
- [ ] Display name: "FinOps Cost Data Analyst Agent"
- [ ] Description added
- [ ] Service account key generated
- [ ] Key stored securely (NOT in git)
- [ ] Key file permissions set to 600 (chmod 600)
- [ ] Key file location documented in .env

### IAM Roles
- [ ] Service account has `roles/bigquery.dataViewer`
  ```bash
  gcloud projects add-iam-policy-binding gac-prod-471220 \
    --member="serviceAccount:finops-agent@gac-prod-471220.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"
  ```

- [ ] Service account has `roles/bigquery.jobUser`
  ```bash
  gcloud projects add-iam-policy-binding gac-prod-471220 \
    --member="serviceAccount:finops-agent@gac-prod-471220.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"
  ```

### Permissions Verification
- [ ] Can list datasets: `bigquery.datasets.get`
- [ ] Can list tables: `bigquery.tables.list`
- [ ] Can read table metadata: `bigquery.tables.get`
- [ ] Can create query jobs: `bigquery.jobs.create`
- [ ] **Cannot** write data (WriteMode.BLOCKED enforced)

### Security Testing
- [ ] Attempted DROP query rejected
- [ ] Attempted DELETE query rejected
- [ ] Attempted INSERT query rejected
- [ ] SQL injection patterns blocked (semicolons, comments)
- [ ] Only SELECT queries allowed

---

## ⚙️ Agent Configuration

### Environment Variables (.env)
- [ ] `.env` file created
- [ ] `.env` added to .gitignore (verify: `git status` should NOT show .env)
- [ ] All required variables set:
  ```bash
  BIGQUERY_PROJECT=gac-prod-471220
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
  ROOT_AGENT_MODEL=gemini-2.0-flash-exp
  ```
- [ ] Optional variables set (if needed):
  ```bash
  BIGQUERY_DATASET=cost_dataset  # Fallback hint
  BIGQUERY_TABLE=cost_analysis   # Fallback hint
  TEMPERATURE=0.01
  LOG_LEVEL=INFO
  ```

### Agent Validation
- [ ] Agent imports successfully
  ```bash
  python3 -c "from agent import root_agent; print(root_agent.name)"
  ```
- [ ] Structure test passes
  ```bash
  python3 test_simple.py
  ```
- [ ] All 4 sub-agents load correctly
- [ ] SQL Generation agent has 4 tools (including list_dataset_ids)
- [ ] BigQuery toolsets configured correctly

---

## 🧪 Testing

### Unit Tests
- [ ] `python3 test_simple.py` passes
- [ ] All assertions pass:
  - [ ] Root agent is SequentialAgent
  - [ ] 4 sub-agents exist
  - [ ] All sub-agents have output_key
  - [ ] SQL Generation has schema toolset (4 tools)
  - [ ] SQL Validation has validation tools (3 tools)
  - [ ] Query Execution has execution toolset (1 tool)
  - [ ] Insight Synthesis has no tools

### Integration Tests (ADK Eval)
- [ ] Eval framework runs: `adk eval --eval-file eval/eval_data/simple.test.json`
- [ ] All test cases pass
- [ ] No errors in logs

### Functional Tests (Manual)

**Test 1: Cost Query (Single Table)**
- [ ] Query: "What is the total cost for February 2025?"
- [ ] Agent discovers `cost_dataset.cost_analysis`
- [ ] SQL generated correctly
- [ ] Results accurate (matches manual query)
- [ ] Response time < 5 seconds

**Test 2: Budget Query (Single Table)**
- [ ] Query: "What is the budget for ML Training?"
- [ ] Agent discovers `budget_dataset.budget`
- [ ] SQL generated correctly
- [ ] Results accurate
- [ ] Response time < 5 seconds

**Test 3: Usage Query (Single Table)**
- [ ] Query: "How many compute hours did we use?"
- [ ] Agent discovers `usage_dataset.resource_usage`
- [ ] SQL generated correctly
- [ ] Results accurate
- [ ] Response time < 5 seconds

**Test 4: Comparison Query (Multi-Table JOIN)**
- [ ] Query: "Compare budget vs actual costs for February 2025"
- [ ] Agent discovers BOTH cost_dataset AND budget_dataset
- [ ] JOIN SQL generated correctly
- [ ] Variance calculated correctly
- [ ] Results accurate
- [ ] Response time < 10 seconds

**Test 5: Error Handling**
- [ ] Invalid SQL rejected (e.g., "DROP TABLE cost_analysis")
- [ ] Validation error message clear
- [ ] Agent recovers gracefully

**Test 6: Dynamic Discovery**
- [ ] Agent lists datasets via `list_dataset_ids`
- [ ] Pattern matching works (selects correct dataset)
- [ ] Schema fetched via `get_table_info`
- [ ] SQL uses correct column names

---

## 📊 Performance Validation

### Query Performance
- [ ] Single-table queries: < 5 seconds (95th percentile)
- [ ] Multi-table JOINs: < 10 seconds (95th percentile)
- [ ] Discovery overhead: < 300ms
- [ ] BigQuery bytes scanned: < 100MB per query (with partitioning)

### Resource Usage
- [ ] Memory usage: < 512MB per query
- [ ] CPU usage: < 1 vCPU per query
- [ ] No memory leaks (test with 100 queries)

---

## 🚀 Deployment

### Local Deployment (Development)
- [ ] ADK web runs from parent directory
  ```bash
  cd /path/to/google-adk-agents
  adk web --port 8000
  ```
- [ ] Agent appears in dropdown
- [ ] Agent loads without errors
- [ ] Test queries work

### Production Deployment (Cloud Run - Optional)
- [ ] Dockerfile created (if needed)
- [ ] Container image built and pushed
- [ ] Cloud Run service deployed
- [ ] Environment variables set
- [ ] Service account attached
- [ ] Health check configured
- [ ] Scaling settings configured (min/max instances)
- [ ] Production URL accessible

---

## 📈 Monitoring & Observability

### Logging
- [ ] Cloud Logging enabled
- [ ] Log sink configured (if needed)
- [ ] Logs include:
  - [ ] User queries
  - [ ] Query classification
  - [ ] Discovered datasets/tables
  - [ ] Generated SQL
  - [ ] Validation results
  - [ ] Query results
  - [ ] Errors

### Metrics
- [ ] Query count tracked
- [ ] Response time tracked (P50, P95, P99)
- [ ] Error rate tracked
- [ ] BigQuery bytes scanned tracked
- [ ] Validation failure rate tracked

### Alerts
- [ ] Alert on high error rate (> 5%)
- [ ] Alert on slow queries (P95 > 10s)
- [ ] Alert on service unavailability
- [ ] Alert recipients configured

### Dashboard
- [ ] Monitoring dashboard created (Looker Studio or similar)
- [ ] Widgets:
  - [ ] Query volume over time
  - [ ] Response time distribution
  - [ ] Error rate
  - [ ] Top users
  - [ ] Most common query types
  - [ ] Cost efficiency (bytes scanned)

---

## 👥 User Onboarding

### Training Materials
- [ ] User guide (README.md) accessible
- [ ] Example queries documented
- [ ] Video demo recorded (optional)
- [ ] FAQ created

### User Access
- [ ] User list finalized
- [ ] Access granted to ADK web UI
- [ ] Users can authenticate
- [ ] Users trained on basic queries

### Feedback Loop
- [ ] Feedback collection mechanism (Slack, email, form)
- [ ] Issue tracking (GitHub Issues, Jira)
- [ ] Regular review meetings scheduled

---

## 🔄 Maintenance & Operations

### Backup & Recovery
- [ ] BigQuery data has backup/snapshot strategy
- [ ] Service account key backed up securely
- [ ] Code versioned in Git
- [ ] .env.example kept up-to-date

### Updates & Patches
- [ ] ADK version documented: `1.16.0+`
- [ ] Python version documented: `3.10+`
- [ ] Dependency versions pinned (requirements.txt)
- [ ] Update process documented

### Data Refresh
- [ ] Data loading schedule defined (daily, weekly, monthly)
- [ ] Data quality checks automated
- [ ] Historical data retention policy defined
- [ ] Data archival process defined

---

## ✅ Go/No-Go Decision

### Critical (Must Pass - Go/No-Go)
- [ ] All 3 datasets exist with correct schemas
- [ ] Service account has correct permissions
- [ ] Agent imports without errors
- [ ] All 4 test query types work
- [ ] Security validation blocks dangerous SQL
- [ ] Response time < 10 seconds for all queries
- [ ] Documentation complete

### High Priority (Should Pass - Go with Caution)
- [ ] ADK eval tests pass
- [ ] Performance metrics within targets
- [ ] Monitoring dashboard created
- [ ] User training complete

### Medium Priority (Nice to Have - Can Deploy)
- [ ] Alerts configured
- [ ] Production deployment automated
- [ ] Feedback loop established

---

## 📝 Deployment Sign-Off

### Development Team
- [ ] Code complete and tested
- [ ] Documentation complete
- [ ] Deployment scripts tested
- **Signed**: ________________ Date: __________

### DevOps/Platform Team
- [ ] Infrastructure provisioned
- [ ] Security reviewed
- [ ] Monitoring configured
- **Signed**: ________________ Date: __________

### FinOps Team (Product Owner)
- [ ] Requirements met
- [ ] User training complete
- [ ] Ready for production use
- **Signed**: ________________ Date: __________

### Security Team
- [ ] IAM permissions reviewed
- [ ] SQL injection protection verified
- [ ] Secrets management verified
- [ ] Audit logging configured
- **Signed**: ________________ Date: __________

---

## 🎉 Post-Deployment

### Day 1
- [ ] Monitor error rates (should be < 1%)
- [ ] Review user queries
- [ ] Address urgent issues
- [ ] Collect initial feedback

### Week 1
- [ ] Review performance metrics
- [ ] Tune prompts if needed
- [ ] Address feedback
- [ ] Expand user base

### Month 1
- [ ] Evaluate for wider rollout
- [ ] Review cost efficiency
- [ ] Plan Phase 3 features (forecasting, insights)
- [ ] Document lessons learned

---

## 📚 Related Documents

- **MIGRATION.md** - Step-by-step setup instructions
- **README.md** - User guide
- **CLAUDE.md** - Developer guide
- **PRD_FinOps_Agent.md** - Product requirements
- **TECHNICAL_ARCHITECTURE.md** - Technical specifications

---

**Deployment Status**: ⏳ Ready for Tomorrow's Setup

**Next Steps**:
1. Follow MIGRATION.md to create datasets and tables
2. Complete this checklist
3. Sign off with all teams
4. Deploy to production

**Version**: 2.0 - Multi-Table Discovery
**Last Updated**: October 21, 2025
