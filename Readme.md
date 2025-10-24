# Google ADK Agents

Multi-agent system built with Google Agent Development Kit (ADK) for FinOps and cloud cost management.

## Project Structure

```
google-adk-agents/
├── finops-cost-data-analyst/    # FinOps Cost Data Analyst Agent
│   ├── CLAUDE.md                # Developer guide
│   ├── Readme.md                # User documentation
│   ├── PRD_FinOps_Agent.md      # Product requirements
│   └── ...                      # Agent-specific files
│
├── .env                         # Environment configuration (gitignored)
├── .env.example                 # Example environment file
└── README.md                    # This file
```

## Agents

### 1. FinOps Cost Data Analyst

**Purpose**: Analyzes cloud cost data from BigQuery using dynamic schema discovery and multi-agent workflow.

**Documentation**: See [finops-cost-data-analyst/](./finops-cost-data-analyst/)

**Quick Start**:
```bash
# From project root
adk web

# In browser: http://localhost:8000
# Select: finops-cost-data-analyst
```

## Requirements

- Python 3.11+
- Google Cloud SDK
- ADK CLI: `pip install google-adk`
- BigQuery access with appropriate IAM permissions

## Configuration

1. Copy `.env.example` to `.env`
2. Set `BIGQUERY_PROJECT` to your GCP project ID
3. Run `gcloud auth application-default login`

## Running ADK Web

```bash
# Always run from project root (google-adk-agents/)
cd /Users/gurukallam/projects/google-adk-agents
adk web

# Access at http://localhost:8000
```

## Development

- Each agent is a separate folder at the project root
- Agent-specific documentation lives inside the agent folder
- Shared resources (like `.env`) are at the project root

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Python Samples](https://github.com/google/adk-python/tree/main/samples)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

## License

Internal use only.
