# FinOps Cost Insights Agent

**Production-Ready Multi-Agent AI System for Cloud Financial Operations**

This project is an enterprise-grade multi-agent AI system built with the **Google Agent Development Kit (ADK)**. It provides a conversational interface for FinOps teams, enabling natural language queries about multi-cloud spending across GCP, AWS, and Azure with accurate, data-backed insights.

The system queries cloud billing data from BigQuery using a secure, orchestrated multi-step workflow managed by specialized AI agents.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![ADK](https://img.shields.io/badge/Google-ADK-4285F4)](https://google.github.io/adk-docs/)

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Data Source & Schema](#data-source--schema)
- [Business Logic](#business-logic)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Query Examples](#query-examples)
- [Security](#security)
- [Evaluation & Testing](#evaluation--testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

### Key Features

- **Multi-Agent Architecture**: Hierarchical orchestration with specialized agents for each workflow stage
- **Natural Language to SQL**: Automatic translation of business questions to optimized BigQuery SQL
- **Multi-Cloud Support**: Unified cost analysis across GCP, AWS, and Azure
- **Enterprise Security**: Zero-trust security model using MCP (Model Context Protocol) Toolbox
- **Production Ready**: Input validation, SQL injection prevention, comprehensive error handling
- **Scalable Design**: Designed for deployment on Vertex AI Agent Engine or Cloud Run
- **Cost Optimization**: Built-in analytics for cost trends, anomalies, and forecasting
- **Chargeback/Showback**: Team, product, and application-level cost attribution

### Use Cases

1. **Executive Reporting**: Monthly cost summaries, YoY comparisons, budget tracking
2. **Cost Optimization**: Identify high-cost services, anomaly detection, waste reduction
3. **Chargeback/Showback**: Allocate costs to teams, products, and environments
4. **Forecasting**: Predict future cloud spending using historical trends
5. **Multi-Cloud Analysis**: Compare costs across cloud providers
6. **Compliance**: Track spending against budgets and compliance requirements

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Google Agent Development Kit (ADK) v1.14+ | Multi-agent orchestration |
| **AI Models** | Google Gemini 2.5 Flash | Natural language understanding, SQL generation |
| **Data Backend** | Google BigQuery | Cloud cost data warehouse |
| **Security** | MCP Toolbox for Databases | Secure, credential-less database access |
| **Deployment** | Vertex AI Agent Engine | Managed, scalable agent hosting |
| **Language** | Python 3.10+ | Core implementation |
| **Dependencies** | google-adk, google-cloud-aiplatform, toolbox-core | Agent runtime |

---

## Architecture

### Multi-Agent Hierarchical System

This project implements a **sequential multi-agent workflow** where each agent has a single, well-defined responsibility. The `OrchestratorAgent` manages the end-to-end flow, passing a shared state object between specialists.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User Query                                      │
│                 "What was GenAI cost in FY26?"                          │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      OrchestratorAgent                                   │
│                    (Sequential Workflow)                                 │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Schema Analyst  │ ──► Fetch table schema via MCP
                    │     Agent       │     describe-table tool
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  SQL Generator  │ ──► Translate NL → SQL with
                    │      Agent      │     business logic
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  SQL Validator  │ ──► Security check: SELECT only,
                    │      Agent      │     no DROP/DELETE/etc
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ BigQuery Exec   │ ──► Execute validated query via
                    │      Agent      │     MCP execute-query tool
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Insight Synth   │ ──► Format results into human-
                    │      Agent      │     readable insights
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Final Answer                                     │
│  "The GenAI cost in FY26 (Feb 2025 - Jan 2026) was $1,234,567.89"     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Roles & Responsibilities

| Agent | Location | Role | Key Responsibilities |
|-------|----------|------|---------------------|
| **OrchestratorAgent** | `agents/orchestrator/` | Team Lead | Manages sequential workflow, coordinates state, returns final response |
| **SchemaAnalystAgent** | `agents/schema_analyst/` | Data Expert | Fetches table schema using MCP `describe-table`, provides context |
| **SQLGenerationAgent** | `agents/sql_generator/` | SQL Engineer | **CRITICAL**: Translates NL to GoogleSQL with business logic enforcement |
| **SQLValidatorAgent** | `agents/sql_validator/` | Security Guard | Validates SQL safety: SELECT only, no injection vectors |
| **BigQueryExecutorAgent** | `agents/bq_executor/` | Query Runner | Executes validated SQL via MCP `execute-query` tool |
| **InsightSynthesizerAgent** | `agents/insight_synthesizer/` | Business Analyst | Transforms raw data into conversational insights |

### Design Principles

1. **Separation of Concerns**: Each agent has ONE job
2. **Zero Trust Security**: No direct database credentials in agent code
3. **Fail-Safe Validation**: Multi-layer security checks before execution
4. **Stateful Orchestration**: Shared state object maintains context across agents
5. **Model Context Protocol**: Standardized tool interfaces for database operations
6. **Testability**: Each agent can be tested in isolation

---

## Data Source & Schema

### BigQuery Table

**Fully Qualified Table Name**: Configured via environment variables (see [Configuration](#configuration))

- **Project**: Set via `BIGQUERY_PROJECT` environment variable
- **Dataset**: Set via `BIGQUERY_DATASET` environment variable
- **Table**: Set via `BIGQUERY_TABLE` environment variable

### Schema Definition

| Field Name | Mode | Type | Description | Example Values |
|------------|------|------|-------------|----------------|
| `date` | REQUIRED | DATE | Date of cost record | `2025-10-15` |
| `cto` | NULLABLE | STRING | Chief Technology Officer / Organization | `Engineering`, `Product`, `Data Science` |
| `cloud` | REQUIRED | STRING | Cloud provider | `GCP`, `AWS`, `Azure` |
| `tr_product_pillar_team` | NULLABLE | STRING | Product pillar or team | `Payments Platform`, `User Services` |
| `tr_subpillar_name` | NULLABLE | STRING | Sub-pillar or sub-team | `Payment Gateway`, `Auth Service` |
| `tr_product_id` | NULLABLE | INTEGER | Product identifier | `1001`, `2045` |
| `tr_product` | NULLABLE | STRING | Product name | `Mobile App`, `Web Platform` |
| `apm_id` | NULLABLE | STRING | Application Performance Monitoring ID | `APM-12345` |
| `application` | REQUIRED | STRING | Application name | `payment-service`, `user-api` |
| `service_name` | NULLABLE | STRING | Service within application | `auth-microservice`, `db-replica` |
| `managed_service` | REQUIRED | STRING | Cloud managed service type | `Compute Engine`, `Cloud Storage`, `RDS`, `AI/ML` |
| `environment` | REQUIRED | STRING | Environment type | `production`, `staging`, `development` |
| `cost` | REQUIRED | FLOAT | Daily cost in USD | `1234.56` |

### Schema DDL

```sql
CREATE TABLE `your-project-id.your_dataset.cost_analysis` (
  date DATE NOT NULL,
  cto STRING,
  cloud STRING NOT NULL,
  application STRING NOT NULL,
  managed_service STRING NOT NULL,
  environment STRING NOT NULL,
  cost FLOAT64 NOT NULL
)
PARTITION BY date
CLUSTER BY cloud, environment, managed_service;
```

**Note**: Replace `your-project-id` and `your_dataset` with your actual BigQuery project and dataset names.

### Data Characteristics

- **Row Count**: ~10M+ rows (grows daily)
- **Date Range**: 2024-02-01 to present
- **Partitioning**: Daily partitions by `date` for query optimization
- **Clustering**: `cloud`, `environment`, `managed_service` for performance
- **Update Frequency**: Daily batch updates (typically 2 AM UTC)
- **Data Retention**: 2+ years historical data

---

## Business Logic

### Critical Business Rules

The `SQLGenerationAgent` enforces these **hard-coded business rules** via system prompts in `agents/sql_generator/prompts.py`:

#### 1. GenAI Cost Mapping

**Rule**: Any query containing "GenAI", "AI cost", or "machine learning cost" MUST filter:

```sql
WHERE managed_service = 'AI/ML'
```

**Examples**:
- User: "What was the GenAI cost last month?"
- SQL: `SELECT SUM(cost) FROM table WHERE managed_service = 'AI/ML' AND date >= '2025-09-01' AND date < '2025-10-01'`

#### 2. Fiscal Year 2026 (FY26) Date Range

**Rule**: Any query for "FY26" MUST translate to:

```sql
WHERE date BETWEEN '2025-02-01' AND '2026-01-31'
```

**Fiscal Year Definition**: February 1 to January 31

#### 3. Fiscal Year 2025 (FY25) Date Range

**Rule**: Any query for "FY25" MUST translate to:

```sql
WHERE date BETWEEN '2024-02-01' AND '2025-01-31'
```

### Why These Rules Matter

- **Consistency**: Ensures all teams use the same definitions for "GenAI" and fiscal years
- **Compliance**: Aligns with company financial reporting standards
- **Accuracy**: Prevents manual calculation errors in executive reports
- **Auditability**: Centralized logic makes it easy to trace decisions

---

## Project Structure

```
finops-cost-data-analyst/
├── README.md                          # This file
├── .mcp.json                          # MCP Toolbox configuration (not in git)
├── .env                               # Environment variables (not in git)
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Python project metadata
├── main.py                            # ADK entry point (root_agent)
│
├── agents/                            # Agent implementations
│   ├── __init__.py
│   │
│   ├── orchestrator/                  # Orchestrator Agent
│   │   ├── __init__.py
│   │   ├── agent.py                   # OrchestratorAgent definition
│   │   └── prompts.py                 # Orchestration prompts
│   │
│   ├── schema_analyst/                # Schema Analyst Agent
│   │   ├── __init__.py
│   │   ├── agent.py                   # SchemaAnalystAgent definition
│   │   └── prompts.py                 # Schema analysis prompts
│   │
│   ├── sql_generator/                 # SQL Generator Agent (CRITICAL)
│   │   ├── __init__.py
│   │   ├── agent.py                   # SQLGenerationAgent definition
│   │   └── prompts.py                 # SQL generation + business logic
│   │
│   ├── sql_validator/                 # SQL Validator Agent
│   │   ├── __init__.py
│   │   ├── agent.py                   # SQLValidatorAgent definition
│   │   └── prompts.py                 # SQL validation rules
│   │
│   ├── bq_executor/                   # BigQuery Executor Agent
│   │   ├── __init__.py
│   │   ├── agent.py                   # BigQueryExecutorAgent definition
│   │   └── prompts.py                 # Execution prompts
│   │
│   └── insight_synthesizer/           # Insight Synthesizer Agent
│       ├── __init__.py
│       ├── agent.py                   # InsightSynthesizerAgent definition
│       └── prompts.py                 # Insight formatting prompts
│
├── tools/                             # Custom tools (if needed)
│   └── __init__.py
│
├── eval/                              # Evaluation & testing
│   ├── __init__.py
│   ├── test_finops_agent.py          # Pytest evaluation tests
│   └── eval_data/                     # Test cases
│       ├── genai_cost.test.json      # GenAI cost test
│       ├── fy26_total.test.json      # FY26 total cost test
│       └── config.json                # Eval configuration
│
├── deployment/                        # Deployment scripts
│   ├── deploy_vertex.py              # Vertex AI deployment
│   ├── deploy_cloudrun.py            # Cloud Run deployment
│   └── Dockerfile                    # Container image
│
└── docs/                              # Additional documentation
    ├── architecture.md                # Detailed architecture
    ├── security.md                    # Security design
    └── api_reference.md               # API reference
```

### Key Files

- **`main.py`**: Entry point defining `root_agent` for ADK
- **`agents/orchestrator/agent.py`**: Main orchestration logic
- **`agents/sql_generator/prompts.py`**: **CRITICAL** - Contains business logic
- **`.mcp.json`**: MCP Toolbox server configuration
- **`requirements.txt`**: Python dependencies

---

## Setup & Installation

### Prerequisites

- **Python**: 3.10 or higher
- **Google Cloud SDK**: `gcloud` CLI installed and authenticated
- **BigQuery Access**: Read permissions on your BigQuery cost analysis table
- **Google GenAI API Key**: For Gemini model access

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/finops-cost-agent.git
cd finops-cost-agent
```

#### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**`requirements.txt` Contents**:
```
google-adk>=1.14
google-cloud-aiplatform[adk,agent-engines]>=1.93.0
google-cloud-bigquery>=3.12.0
toolbox-core>=0.3.0
python-dotenv>=1.0.1
pydantic>=2.11.3
pytest>=8.3.5
pytest-asyncio>=0.26.0
```

#### 4. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

#### 5. Download MCP Toolbox Binary

**Option A: Direct Download**
```bash
export OS="darwin/arm64"  # Options: linux/amd64, darwin/arm64, darwin/amd64, windows/amd64
curl -O https://storage.googleapis.com/genai-toolbox/v0.12.0/$OS/toolbox
chmod +x toolbox
mv toolbox /usr/local/bin/  # Or keep in project root
```

**Option B: Use Existing Installation**
```bash
which toolbox  # Verify toolbox is on PATH
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root (use `.env.example` as template):

```bash
# Google GenAI API Configuration
GOOGLE_API_KEY=your-google-api-key-here

# Google Cloud Configuration (for BigQuery via service account)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery Configuration
BIGQUERY_PROJECT=your-bigquery-project-id
BIGQUERY_DATASET=your_dataset_name
BIGQUERY_TABLE=cost_analysis

# Model Configuration
ROOT_AGENT_MODEL=gemini-2.0-flash-exp
SQL_GENERATOR_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.01

# Logging
LOG_LEVEL=INFO
```

**Important Notes**:
- Replace all `your-*` placeholders with your actual values
- See `.env.example` for a complete template
- The `.env` file should never be committed to version control

### BigQuery Authentication

This agent uses service account authentication for BigQuery access. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account JSON key file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

Or add it to your `.env` file as shown above.

---

## Usage Examples

### Running Locally

#### 1. Start ADK Web Interface

```bash
adk web
```

Open browser to: `http://localhost:8000`

#### 2. Example Interactions

**Query 1: GenAI Cost in FY26**
```
User: What was the total GenAI cost in FY26?

Agent: The total GenAI cost in FY26 (February 2025 - January 2026)
       was $1,234,567.89.
```

**Query 2: Top 5 Applications**
```
User: Show me the top 5 most expensive applications last month

Agent: Here are the top 5 applications by cost in September 2025:
       1. payment-service: $45,678.90
       2. user-api: $34,567.80
       3. data-pipeline: $23,456.70
       4. ml-training: $12,345.60
       5. web-frontend: $11,234.50
```

**Query 3: Cloud Provider Comparison**
```
User: Compare costs across GCP, AWS, and Azure for Q3 2025

Agent: Cloud cost comparison for Q3 2025 (July-September):
       - GCP: $567,890.12 (45%)
       - AWS: $432,109.87 (34%)
       - Azure: $265,432.10 (21%)
       Total: $1,265,432.09
```

### Running via CLI

```bash
# Interactive CLI mode
adk run

# Single query mode
adk query "What was the GenAI cost in FY26?"
```

---

## Query Examples

### Cost Analysis Queries

```sql
-- Total cost by cloud provider (last 30 days)
SELECT
  cloud,
  SUM(cost) as total_cost
FROM `your-project.your_dataset.cost_analysis`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY cloud
ORDER BY total_cost DESC;

-- Top 10 applications by cost (current month)
SELECT
  application,
  SUM(cost) as total_cost
FROM `your-project.your_dataset.cost_analysis`
WHERE date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY application
ORDER BY total_cost DESC
LIMIT 10;

-- GenAI cost trend (FY26)
SELECT
  DATE_TRUNC(date, MONTH) as month,
  SUM(cost) as monthly_cost
FROM `your-project.your_dataset.cost_analysis`
WHERE
  managed_service = 'AI/ML'
  AND date BETWEEN '2025-02-01' AND '2026-01-31'
GROUP BY month
ORDER BY month;
```

**Note**: Replace `your-project.your_dataset` with your actual BigQuery project and dataset names (or use environment variable references).

### Natural Language Query Examples

**Cost Trends**:
- "What's the daily cost trend for the last week?"
- "Show me month-over-month cost growth for 2025"
- "What was the cost on October 15th, 2025?"

**Optimization**:
- "Which services cost more than $10,000 last month?"
- "Find applications with cost increases over 50% this quarter"
- "What are the most expensive managed services in GCP?"

**Chargeback/Showback**:
- "Total cost per CTO for Q3 2025"
- "Break down costs by product pillar team"
- "Cost allocation by environment (prod vs staging)"

**Multi-Cloud**:
- "Compare GCP vs AWS costs this year"
- "What percentage of total cost is Azure?"
- "Show me cloud cost distribution"

**Forecasting**:
- "Based on current trends, what will next month's cost be?"
- "Projected annual spend for GenAI services"
- "Cost forecast for Q4 2025"

---

## Security

### Zero-Trust Architecture

This agent implements a **zero-trust security model**:

1. **No Direct Credentials**: Agent code never handles database credentials
2. **MCP Broker Pattern**: All database access is mediated by MCP Toolbox
3. **Application Default Credentials**: MCP server uses ADC for auth
4. **Least Privilege**: Agents only have access to pre-defined tools
5. **SQL Injection Prevention**: Multi-layer validation before execution

### Security Layers

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: User Input Validation                               │
│ - Schema validation in SchemaAnalystAgent                    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: SQL Generation with Business Logic                  │
│ - Template-based SQL generation                              │
│ - Parameterized queries                                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: SQL Validation (SQLValidatorAgent)                  │
│ - SELECT-only enforcement                                    │
│ - Forbidden keyword detection (DROP, DELETE, etc.)           │
│ - Syntax validation                                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 4: MCP Toolbox Execution Boundary                      │
│ - No direct database access from agent                       │
│ - MCP server validates query before execution                │
│ - ADC authentication                                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 5: BigQuery IAM & VPC                                  │
│ - IAM role-based access control                              │
│ - VPC Service Controls (optional)                            │
│ - Query audit logging                                        │
└──────────────────────────────────────────────────────────────┘
```

### SQL Validation Rules

The `SQLValidatorAgent` enforces:

- ✅ **Allowed**: `SELECT`, `WITH`, `FROM`, `WHERE`, `GROUP BY`, `ORDER BY`, `LIMIT`
- ❌ **Forbidden**: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `CREATE`, `ALTER`, `GRANT`, `REVOKE`
- ❌ **Forbidden**: `;` (prevents statement chaining)
- ❌ **Forbidden**: `--`, `/**/` (prevents comment injection)

### IAM Permissions Required

**For Local Development**:
```
roles/bigquery.dataViewer       # Read table data
roles/bigquery.jobUser          # Run queries
```

**For Service Account** (via GOOGLE_APPLICATION_CREDENTIALS):
```
roles/bigquery.dataViewer       # Read table data
roles/bigquery.jobUser          # Run queries
```

---

## Evaluation & Testing

### Test Structure

```
eval/
├── test_finops_agent.py          # Pytest test runner
└── eval_data/
    ├── genai_fy26.test.json      # GenAI + FY26 test
    ├── top_apps.test.json        # Top applications test
    ├── cloud_comparison.test.json # Multi-cloud test
    └── config.json                # Test configuration
```

### Running Tests

```bash
# Run all evaluation tests
pytest eval/test_finops_agent.py -v

# Run specific test
pytest eval/test_finops_agent.py::test_genai_fy26 -v

# Run with detailed output
pytest eval/test_finops_agent.py -v -s

# Generate coverage report
pytest eval/ --cov=agents --cov-report=html
```

### Example Test Case

**`eval/eval_data/genai_fy26.test.json`**:
```json
{
  "query": "What was the total GenAI cost in FY26?",
  "expected_response_contains": [
    "GenAI",
    "FY26",
    "February 2025",
    "January 2026"
  ],
  "expected_sql_contains": [
    "managed_service = 'AI/ML'",
    "date BETWEEN '2025-02-01' AND '2026-01-31'"
  ]
}
```

### ADK Web UI Evaluation

1. Navigate to `http://localhost:8000`
2. Click **Eval** tab
3. Create new eval set
4. Upload test cases from `eval/eval_data/`
5. Run evaluation
6. View pass/fail results

---

## Deployment

### Vertex AI Agent Engine (Recommended)

#### 1. Build Deployment Package

```bash
# Create wheel file
uv build --wheel --out-dir deployment

# Or use setuptools
python -m build --wheel --outdir deployment
```

#### 2. Deploy to Vertex AI

```bash
cd deployment
python deploy_vertex.py --create

# Example output:
# Agent deployed: projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/1234567890
```

#### 3. Test Deployment

```bash
export RESOURCE_ID=1234567890
export USER_ID=test-user
python deployment/test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

### Google Cloud Run

#### 1. Build Container Image

```bash
docker build -t gcr.io/YOUR_PROJECT/finops-agent:latest .
docker push gcr.io/YOUR_PROJECT/finops-agent:latest
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy finops-agent \
  --image gcr.io/YOUR_PROJECT/finops-agent:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT \
  --allow-unauthenticated
```

---

## Troubleshooting

### Common Issues

#### 1. BigQuery Permission Denied

**Error**: `403 Forbidden: Access Denied`

**Solution**:
```bash
# Verify service account authentication
echo $GOOGLE_APPLICATION_CREDENTIALS

# Check that service account has required BigQuery permissions:
# - roles/bigquery.dataViewer
# - roles/bigquery.jobUser
```

#### 2. SQL Validation Failure

**Error**: `SQL validation failed: forbidden keyword detected`

**Solution**:
- Check `SQLValidatorAgent` logs
- Verify generated SQL is SELECT-only
- Review `agents/sql_generator/prompts.py` for business logic

#### 3. Incorrect Business Logic

**Error**: GenAI query not filtering on `managed_service = 'AI/ML'`

**Solution**:
```bash
# Check SQL Generator prompt
cat agents/sql_generator/prompts.py | grep "AI/ML"

# Add/update business logic in prompts.py
# Re-run agent
```

---

## Best Practices

### For Developers

1. **Never Modify Schema**: The `cost_analysis` table is managed by FinOps team
2. **Test Business Logic**: Always add eval tests for new business rules
3. **Use Type Hints**: Maintain strong typing for better error detection
4. **Log Everything**: Use structured logging for debugging
5. **Version Control Prompts**: Treat `prompts.py` files as critical code

### For FinOps Teams

1. **Document Business Logic**: Update README when adding fiscal rules
2. **Test Before Deploy**: Run full eval suite before production deployment
3. **Monitor Query Costs**: BigQuery queries are billed to your project
4. **Set Budget Alerts**: Configure BigQuery budget alerts
5. **Regular Eval Updates**: Keep test cases in sync with business changes

### For Security Teams

1. **Review SQL Validator**: Audit `SQLValidatorAgent` regularly
2. **MCP Server Isolation**: Run MCP Toolbox in separate service account
3. **Audit Logs**: Enable BigQuery audit logging
4. **VPC Service Controls**: Consider adding for production
5. **Regular Penetration Testing**: Test for SQL injection vectors

---

## Contributing

### Development Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-business-rule`
3. Add eval tests for new functionality
4. Update prompts in `agents/*/prompts.py`
5. Run tests: `pytest eval/ -v`
6. Submit PR with description of business logic changes

### Code Style

- **Black**: Code formatting (`black .`)
- **isort**: Import sorting (`isort .`)
- **mypy**: Type checking (`mypy agents/`)
- **pylint**: Linting (`pylint agents/`)

---

## License

Apache License 2.0 - See [LICENSE](LICENSE) file

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/finops-cost-agent/issues)
- **Slack**: `#finops-agent-support`
- **FinOps Team**: finops@yourcompany.com
- **ADK Documentation**: [Google ADK Docs](https://google.github.io/adk-docs/)

---

## Changelog

### v1.0.0 (2025-10-20)
- ✅ Initial production release
- ✅ Multi-agent architecture implementation
- ✅ GenAI cost and FY26/FY25 business logic
- ✅ MCP Toolbox integration
- ✅ Comprehensive test suite
- ✅ Vertex AI deployment support

---

**Built with ❤️ by the FinOps Engineering Team**
