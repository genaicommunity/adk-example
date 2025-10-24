# Product Requirements Document (PRD)
# FinOps Cost Data Analyst Agent

**Version**: 2.0
**Date**: October 21, 2025
**Product Owner**: FinOps Team
**Status**: Dynamic Multi-Table Discovery - Production Ready

---

## 📋 Executive Summary

The **FinOps Cost Data Analyst Agent** is an enterprise-grade AI-powered conversational interface for cloud financial operations. It enables stakeholders to query cost, budget, and usage data using natural language, automatically discovering and routing queries to the appropriate BigQuery datasets without manual configuration.

### Key Innovation
Unlike traditional SQL agents with hardcoded schemas, this agent **dynamically discovers** datasets and tables at runtime, making it portable, self-healing, and capable of handling multiple data sources intelligently.

---

## 🎯 Product Vision

**Enable every stakeholder in the organization to access financial insights instantly through natural language, eliminating the need for SQL expertise or manual data navigation.**

---

## 👥 User Personas

### 1. FinOps Manager (Primary)
- **Role**: Oversees cloud financial operations
- **Pain Points**:
  - Needs quick answers to cost questions
  - Lacks SQL expertise
  - Manually combines data from multiple sources
- **Goals**:
  - Real-time visibility into spending
  - Budget vs actual comparisons
  - Resource utilization insights

### 2. Engineering Lead
- **Role**: Manages application teams and cloud resources
- **Pain Points**:
  - Doesn't have time to write SQL queries
  - Needs to track team spending
  - Must forecast resource needs
- **Goals**:
  - Team cost attribution
  - Trend analysis
  - Anomaly detection

### 3. CFO / Finance Executive
- **Role**: Strategic financial planning
- **Pain Points**:
  - Requires high-level summaries
  - Needs variance analysis (budget vs actual)
  - Must report to board
- **Goals**:
  - Fiscal year summaries
  - Cost optimization opportunities
  - ROI analysis

### 4. Cloud Architect
- **Role**: Infrastructure optimization
- **Pain Points**:
  - Needs detailed usage metrics
  - Must correlate cost with utilization
  - Identifies waste
- **Goals**:
  - Right-sizing recommendations
  - Unused resource identification
  - Cost-per-unit analysis

---

## 📊 User Stories

### Epic 1: Cost Analysis
```
As a FinOps Manager
I want to ask "What is our total cloud cost for FY26?"
So that I can quickly understand our spending
```

**Acceptance Criteria**:
- ✅ Agent discovers cost dataset automatically
- ✅ Returns accurate sum of costs for fiscal year
- ✅ Includes breakdown by cloud provider
- ✅ Response time < 5 seconds

### Epic 2: Budget Management
```
As a CFO
I want to ask "What is our budget vs actual spending for Q2?"
So that I can track financial performance
```

**Acceptance Criteria**:
- ✅ Agent discovers both cost and budget datasets
- ✅ Generates JOIN query automatically
- ✅ Shows variance (over/under budget)
- ✅ Highlights significant deviations

### Epic 3: Resource Utilization
```
As a Cloud Architect
I want to ask "How many compute hours did we use this month?"
So that I can optimize resource allocation
```

**Acceptance Criteria**:
- ✅ Agent discovers usage dataset
- ✅ Aggregates usage metrics correctly
- ✅ Supports different resource types
- ✅ Provides time-based trends

### Epic 4: Multi-Source Analysis
```
As an Engineering Lead
I want to ask "Compare actual costs vs budget vs usage for my application"
So that I can optimize both spending and efficiency
```

**Acceptance Criteria**:
- ✅ Agent queries all 3 datasets (cost, budget, usage)
- ✅ Performs 3-way JOIN automatically
- ✅ Calculates derived metrics (cost per hour, etc.)
- ✅ Identifies optimization opportunities

---

## ✨ Features & Capabilities

### Core Features (v2.0)

#### 1. Dynamic Table Discovery ⚡
- **Capability**: Automatically discovers datasets and tables in BigQuery
- **Tools Used**: `list_dataset_ids`, `list_table_ids`
- **Benefit**: Zero configuration for new tables

#### 2. Intelligent Query Routing
- **Capability**: Classifies user intent (cost/budget/usage) and routes to appropriate table
- **Algorithm**: Pattern matching on dataset/table names
- **Benefit**: Users don't need to know table locations

#### 3. Dynamic Schema Discovery
- **Capability**: Fetches table schema at runtime via `get_table_info`
- **Benefit**: Self-healing when schema changes

#### 4. Multi-Table JOIN Support
- **Capability**: Automatically generates JOIN queries for comparison analysis
- **Example**: Budget vs Actual variance analysis
- **Benefit**: Correlates data across sources

#### 5. Security-First Architecture
- **Validation**: SQL injection prevention via keyword blocking
- **Permissions**: Read-only access (WriteMode.BLOCKED)
- **Audit**: All queries logged for compliance

#### 6. Business Logic Enforcement
- **Fiscal Year Handling**: Automatic FY26/FY25 date range mapping
- **GenAI Filtering**: Recognizes AI/ML cost queries
- **Current Period**: Dynamic date calculations

---

## 🎯 Use Cases

### Use Case 1: Daily Cost Check
**Actor**: FinOps Manager
**Frequency**: Daily
**Query**: "What was our cloud spending yesterday?"

**Flow**:
1. User asks question in natural language
2. Agent classifies as COST query
3. Discovers cost_dataset.cost_analysis table
4. Gets schema dynamically
5. Generates SQL with date filter
6. Executes and returns formatted result

**Expected Response**:
```
Yesterday's cloud spending was $45,234.56.

Breakdown by cloud provider:
- AWS: $28,500.00 (63%)
- GCP: $12,000.00 (27%)
- Azure: $4,734.56 (10%)
```

### Use Case 2: Budget Variance Analysis
**Actor**: CFO
**Frequency**: Monthly
**Query**: "Are we over budget for FY26?"

**Flow**:
1. Agent classifies as COMPARISON query
2. Discovers both cost_dataset and budget_dataset
3. Gets schemas for both tables
4. Generates JOIN query
5. Calculates variance
6. Returns analysis

**Expected Response**:
```
FY26 Budget Status (as of Oct 21, 2025):

Actual Spending: $27,442,275.64
Allocated Budget: $30,000,000.00
Variance: -$2,557,724.36 (8.5% under budget)

Status: ✅ ON TRACK

Applications over budget:
1. ML Training Platform: +$500,000 (15% over)
2. Data Pipeline: +$200,000 (8% over)
```

### Use Case 3: Resource Utilization Analysis
**Actor**: Cloud Architect
**Frequency**: Weekly
**Query**: "Show me compute hours vs costs"

**Flow**:
1. Agent classifies as MULTI-SOURCE query
2. Discovers usage_dataset and cost_dataset
3. Joins on application + date
4. Calculates cost-per-hour metric
5. Returns efficiency analysis

**Expected Response**:
```
Compute Efficiency Analysis (Last 30 Days):

Total Compute Hours: 1,250,000
Total Compute Costs: $156,000
Average Cost/Hour: $0.1248

Most Efficient Applications:
1. Web Frontend: $0.08/hour
2. API Gateway: $0.10/hour

Least Efficient (Review for Optimization):
1. ML Training: $0.45/hour (3.6x avg)
2. Data Processing: $0.25/hour (2x avg)
```

---

## 📈 Success Metrics

### Adoption Metrics
- **Target Users**: 50 monthly active users by Q1 2026
- **Query Volume**: 500+ queries/month
- **User Satisfaction**: > 4.5/5 rating

### Performance Metrics
- **Response Time**: < 5 seconds for 95% of queries
- **Accuracy**: > 98% correct SQL generation
- **Availability**: 99.9% uptime

### Business Impact
- **Time Savings**: 10 hours/week saved per FinOps analyst
- **Query Complexity**: Handle 3+ table JOINs automatically
- **Self-Service Adoption**: 80% of queries answered without data team

---

## 🛠️ Technical Requirements

### Infrastructure
- **GCP Project**: gac-prod-471220
- **BigQuery Datasets**: 3 (cost, budget, usage)
- **ADK Version**: 1.16.0+
- **Python Version**: 3.10+

### Data Requirements

#### Dataset 1: Cost Analysis
```sql
CREATE TABLE `gac-prod-471220.cost_dataset.cost_analysis` (
  date DATE,
  cto STRING,
  cloud STRING,
  application STRING,
  managed_service STRING,
  environment STRING,
  cost FLOAT64
);
```

#### Dataset 2: Budget
```sql
CREATE TABLE `gac-prod-471220.budget_dataset.budget` (
  date DATE,
  application STRING,
  budget_amount FLOAT64,
  fiscal_year STRING,
  department STRING
);
```

#### Dataset 3: Resource Usage
```sql
CREATE TABLE `gac-prod-471220.usage_dataset.resource_usage` (
  date DATE,
  resource_type STRING,
  application STRING,
  usage_hours FLOAT64,
  usage_amount FLOAT64
);
```

### IAM Permissions
**Required**:
- `bigquery.datasets.get`
- `bigquery.tables.get`
- `bigquery.tables.list`
- `bigquery.jobs.create`

**Recommended Service Account**: `finops-agent@gac-prod-471220.iam.gserviceaccount.com`

---

## 🚀 Roadmap

### Phase 1: ✅ Completed (Oct 2025)
- [x] Dynamic schema discovery
- [x] Single-table queries
- [x] Security validation
- [x] Basic insights

### Phase 2: ✅ Current (Oct 2025)
- [x] Multi-table discovery
- [x] Intelligent query routing
- [x] JOIN query support
- [x] Pattern matching

### Phase 3: ✅ Completed (Oct 2025)
- [x] BigQuery AI integration (forecasting)
- [x] Natural language insights (ask_data_insights)
- [x] Anomaly detection (SQL-based + ML-based)
- [x] Prompt-guided ML tool usage

### Phase 4: Future (2026)
- [ ] Real-time alerts
- [ ] Dashboard generation
- [ ] Policy enforcement
- [ ] Multi-cloud support (AWS Cost Explorer, Azure Cost Management)

---

## 🎓 Non-Functional Requirements

### Scalability
- Support 100+ concurrent users
- Handle datasets with 10M+ rows
- Sub-5-second query response time

### Security
- Zero-trust architecture
- Read-only database access
- SQL injection prevention
- Audit logging for compliance

### Reliability
- 99.9% uptime SLA
- Automatic failover
- Error recovery with helpful messages

### Maintainability
- Self-documenting code
- Comprehensive test coverage
- Automated deployments

---

## 📝 Out of Scope (v2.0)

- ❌ Write operations (INSERT, UPDATE, DELETE)
- ❌ Direct database modifications
- ❌ Custom ML model training
- ❌ Real-time streaming data
- ❌ Multi-cloud billing consolidation (coming in v3.0)

---

## ✅ Acceptance Criteria (v2.0 Release)

### Must Have
- [x] Dynamic discovery of 3 datasets (cost, budget, usage)
- [x] Intelligent query routing based on user intent
- [x] Multi-table JOIN support
- [x] < 5 second response time for single-table queries
- [x] > 95% SQL generation accuracy
- [x] Comprehensive documentation

### Should Have
- [x] Pattern matching for dataset/table discovery
- [x] Schema caching for performance
- [x] Detailed error messages

### Could Have
- [ ] Natural language insights (deferred to Phase 3)
- [ ] Forecasting capabilities (deferred to Phase 3)
- [ ] Dashboard generation (deferred to Phase 4)

---

## 📚 Dependencies

### External Services
- Google BigQuery
- Google ADK
- Google Gemini API

### Internal Systems
- GCP IAM
- BigQuery datasets (3)
- Service account credentials

---

## 🔒 Security & Compliance

### Data Protection
- No PII in queries
- Results filtered for authorized users only
- Audit trail for all queries

### Compliance
- SOC 2 Type II ready
- GDPR compliant (no personal data)
- FinOps Foundation best practices

---

## 📞 Support & Training

### Documentation
- README.md - User guide
- CLAUDE.md - Developer guide
- PRD (this document) - Product requirements
- Technical Architecture (companion document)

### Training Plan
- Week 1: FinOps team onboarding
- Week 2: Finance team demo
- Week 3: Engineering leads workshop
- Week 4: Self-service rollout

---

## 🎉 Launch Plan

### Pre-Launch (Week -1)
- [ ] Create all 3 BigQuery datasets
- [ ] Load sample data
- [ ] Configure service account
- [ ] Deploy to staging

### Launch (Week 0)
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Gather initial feedback
- [ ] Iterate on prompts

### Post-Launch (Week +1 to +4)
- [ ] User interviews
- [ ] Performance tuning
- [ ] Documentation updates
- [ ] Feature refinement

---

**Approved By**:
- Product: ________________
- Engineering: ________________
- FinOps: ________________
- Security: ________________

**Document Version History**:
- v1.0 (Oct 15, 2025): Initial release - Single table support
- v2.0 (Oct 21, 2025): Multi-table dynamic discovery
- v2.1 (Oct 23, 2025): Added technical architecture, modular refactoring, edge case handling
- v2.2 (Oct 23, 2025): Integrated ML-based anomaly detection (forecast, ask_data_insights) with prompt guidance

---

## 🏗️ Technical Architecture

### System Overview

The agent uses a **Sequential Multi-Agent Architecture** with 4 specialized sub-agents:

```
User Query → Root Agent (Orchestrator)
                ↓
        [Shared State Dictionary]
                ↓
    ┌───────────┴────────────┐
    ↓           ↓            ↓
Agent 1:    Agent 2:     Agent 3:     Agent 4:
SQL Gen  →  Validate  →  Execute  →  Synthesize
(discover)  (security)   (BigQuery)  (insights)
```

### Code Organization

```
finops-cost-data-analyst/
├── agent.py          - Root SequentialAgent (52 lines)
├── sub_agents.py     - 4 specialized agents (124 lines)
├── prompts.py        - Business logic (600 lines)
└── _tools/
    ├── validation_tools.py - SQL security
    └── bigquery_tools.py   - Data access
```

**Design Principles**:
- **Modularity**: Each agent has single responsibility
- **State-Based Flow**: Explicit data passing via `output_key`
- **Dynamic Discovery**: Runtime schema fetching (no hardcoding)
- **Security First**: Read-only operations, SQL validation

### Multi-Agent Workflow

| Agent | Purpose | Tools | Output |
|-------|---------|-------|--------|
| **SQL Generation** | Convert NL to SQL | BigQuery schema discovery | `state['sql_query']` |
| **SQL Validation** | Security checks | Forbidden keywords, parser | `state['validation_result']` |
| **Query Execution** | Run on BigQuery | BigQuery execution | `state['query_results']` |
| **Insight Synthesis** | Format results | None (pure LLM) | `state['final_insights']` |

### Dynamic Schema Discovery

**How It Works**:
1. User asks: "Compare budget vs actual costs"
2. Agent classifies intent: COMPARISON (needs 2 tables)
3. Discovers datasets: `list_dataset_ids()` → ["cost_dataset", "budget_dataset", ...]
4. Matches to intent: cost_dataset + budget_dataset
5. Gets schemas: `get_table_info()` for both tables
6. Generates JOIN query using discovered schema
7. Executes and returns formatted results

**Benefits**:
- ✅ Works with any BigQuery project (portable)
- ✅ Adapts to schema changes automatically
- ✅ Discovers new tables without code changes
- ✅ Generates multi-table JOINs intelligently

### Security Architecture

| Layer | Protection | Implementation |
|-------|------------|----------------|
| SQL Validation | Blocks dangerous keywords | DROP, DELETE, INSERT, UPDATE forbidden |
| Read-Only Mode | No write operations | BigQuery WriteMode.BLOCKED |
| Injection Prevention | SQL parsing | Validates syntax before execution |
| Authentication | Secure access | Google Application Default Credentials |

### Edge Case Handling

The system handles common edge cases automatically:

- **Random Sampling**: `TABLESAMPLE SYSTEM` for "show me 5 random rows"
- **NULL Values**: `COALESCE(SUM(cost), 0)` prevents NULL returns
- **Division by Zero**: `CASE WHEN` guards for cost-per-unit calculations
- **Large Results**: Auto `LIMIT 10,000` to prevent crashes
- **Empty Results**: User-friendly explanations
- **Schema Errors**: Clear error messages with suggestions

### Deployment

**Runtime**: Python 3.11+, Google ADK
**Model**: Gemini 2.0 Flash Exp (configurable)
**Data**: BigQuery with dynamic discovery
**Auth**: Google Application Default Credentials

**Startup**: Single command - `adk web --port 8000`

### Performance

- **Query Response**: < 5 seconds (typical)
- **Schema Discovery**: ~200-300ms per table
- **Concurrent Users**: Supported by ADK web server
- **Scalability**: Unlimited datasets/tables (dynamic)

---

## 📚 Related Documentation

- **TECHNICAL_IMPLEMENTATION_EXECUTIVE_SUMMARY.md**: 2-page technical overview for executives
- **Readme.md**: Comprehensive user and developer guide
- **CLAUDE.md**: Detailed developer reference
- **MIGRATION.md**: 5-minute setup guide
- **ANOMALY_DETECTION.md**: ML-based anomaly detection feature guide
