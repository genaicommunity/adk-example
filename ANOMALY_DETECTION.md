# FinOps Agent - Anomaly Detection Capabilities

**Status**: ✅ **ENABLED** - BigQuery AI Features Active
**Date**: October 22, 2025
**Version**: 2.1 - ML-Based Anomaly Detection

---

## 🎯 What's New

Your FinOps Cost Data Analyst Agent now has **ML-powered anomaly detection** using BigQuery AI features:

1. **`forecast()`** - Time series forecasting for cost predictions
2. **`ask_data_insights()`** - Natural language insights about data patterns

These features complement the existing SQL-based analytics to provide **enterprise-grade anomaly detection**.

---

## 📊 Two Levels of Anomaly Detection

### Level 1: SQL-Based Anomaly Detection (Already Working)

The agent can detect anomalies using standard SQL analytics:

**Example Queries**:
```
"Find applications where February 2025 costs are 50% higher than January 2025"

"Show me services where costs spiked in the last 7 days"

"Which applications have the highest cost variance over the past 3 months?"

"Identify any unusual spending patterns in February 2025"
```

**How It Works**:
1. Agent analyzes your question
2. Generates SQL with window functions, aggregations, and comparisons
3. Executes query on BigQuery
4. Returns anomalies with context

**Best For**:
- Simple threshold-based alerts
- Comparing periods (month-over-month, week-over-week)
- Identifying top outliers
- Quick anomaly checks

---

### Level 2: ML-Based Anomaly Detection (NEW - Just Enabled!)

The agent now uses **BigQuery AI** for advanced anomaly detection:

#### A. Time Series Forecasting with `forecast()`

Predicts future costs and detects deviations from expected patterns.

**Example Queries**:
```
"Forecast cost trends for the next 30 days and identify any applications deviating from the forecast"

"Use ML to predict expected costs for March 2025 and compare against actual spending"

"Which applications are likely to exceed budget based on ML forecasts?"

"Show me cost forecasting with confidence intervals"
```

**How It Works**:
1. Agent calls BigQuery's `ML.FORECAST()` function
2. Uses ARIMA time series models trained on your historical data
3. Returns predictions with confidence intervals
4. Highlights deviations from forecast

**Best For**:
- Trend analysis and forecasting
- Detecting unusual patterns (seasonality, trends)
- Predictive budget alerts
- Capacity planning

---

#### B. Natural Language Insights with `ask_data_insights()`

Gets AI-generated insights about your cost data using natural language.

**Example Queries**:
```
"What insights can BigQuery AI provide about cost anomalies in February 2025?"

"Ask BigQuery AI: Are there any unusual spending patterns in my cost data?"

"Use ML to analyze cost trends and highlight anomalies"

"What does BigQuery AI say about our cloud spending efficiency?"
```

**How It Works**:
1. Agent calls BigQuery's `ask_data_insights()` function
2. BigQuery AI analyzes your data using Gemini models
3. Returns natural language insights about patterns, outliers, correlations
4. Agent synthesizes insights into final report

**Best For**:
- Exploratory data analysis
- Finding hidden patterns
- Correlations between dimensions (cloud, application, service)
- Executive summaries

---

## 🧪 Test Queries for Anomaly Detection

### Quick Tests (Use in ADK Web UI)

**1. Basic SQL Anomaly Detection**:
```
"Find applications with costs above $10,000 in February 2025"
```
→ Uses: SQL aggregation (Level 1)

**2. ML Forecasting**:
```
"Forecast total costs for the next 14 days"
```
→ Uses: BigQuery `ML.FORECAST()` (Level 2A)

**3. Natural Language Insights**:
```
"What insights can you provide about cost anomalies?"
```
→ Uses: BigQuery `ask_data_insights()` (Level 2B)

**4. Combined Approach**:
```
"Use ML to forecast costs for next month, compare with budget, and identify anomalies"
```
→ Uses: Multi-table JOINs + ML forecasting + comparison logic

---

## 🔧 Technical Implementation

### BigQuery Tools Now Available

The SQL Generation Agent now has access to:

| Tool | Purpose | Anomaly Detection Use Case |
|------|---------|----------------------------|
| `get_table_info` | Schema discovery | Identify available cost columns |
| `get_dataset_info` | Dataset metadata | Find cost vs budget datasets |
| `list_table_ids` | List tables | Discover all cost data sources |
| `list_dataset_ids` | List datasets | Multi-dataset anomaly analysis |
| **`forecast`** | **ML forecasting** | **Predict costs, detect deviations** |
| **`ask_data_insights`** | **AI insights** | **Find patterns, anomalies** |

### Toolset Configuration

Located in `_tools/bigquery_tools.py`:

```python
bigquery_full_toolset = BigQueryToolset(
    tool_filter=[
        # Schema Discovery Tools
        "get_table_info",      # Get table metadata including schema
        "get_dataset_info",    # Get dataset metadata
        "list_table_ids",      # List all tables in dataset
        "list_dataset_ids",    # List all datasets in project
        # AI Analytics Tools (NEW!)
        "forecast",            # BigQuery AI time series forecasting
        "ask_data_insights",   # Natural language data insights
    ],
    bigquery_tool_config=bigquery_tool_config,
)
```

Used in `agent.py` line 51:
```python
sql_generation_agent = LlmAgent(
    tools=[bigquery_full_toolset],  # Full toolset with AI features
    ...
)
```

---

## 📈 Example Use Cases

### 1. Monthly Budget Overrun Detection

**User Query**:
```
"Which applications exceeded their monthly budget in February 2025 and are likely to continue exceeding in March based on ML forecasts?"
```

**Agent Workflow**:
1. Discovers cost and budget datasets via `list_dataset_ids()`
2. Fetches schemas via `get_table_info()`
3. Generates SQL JOIN to compare actual vs budget
4. Uses `ML.FORECAST()` to predict March costs
5. Identifies applications likely to exceed budget
6. Returns ranked list with forecast confidence intervals

---

### 2. Anomalous Cost Spike Investigation

**User Query**:
```
"Find cost anomalies in February 2025 and provide insights on what might be causing them"
```

**Agent Workflow**:
1. Generates SQL to calculate daily costs
2. Uses window functions to detect spikes (>2 standard deviations)
3. Calls `ask_data_insights()` to analyze patterns
4. Returns:
   - List of anomalous dates/applications
   - AI insights about correlations (cloud, service, application)
   - Recommendations for investigation

---

### 3. Forecasting-Based Capacity Planning

**User Query**:
```
"Forecast compute costs for next quarter and identify if any applications need budget adjustments"
```

**Agent Workflow**:
1. Discovers usage and cost datasets
2. Filters for compute-related services
3. Uses `ML.FORECAST()` with 90-day horizon
4. Compares forecast against quarterly budget allocations
5. Returns:
   - Forecast chart with confidence intervals
   - Applications likely to exceed budget
   - Recommended budget adjustments

---

## 🚀 Getting Started

### 1. Prerequisites

- ✅ BigQuery datasets created (cost, budget, usage)
- ✅ Historical data loaded (at least 30 days recommended for ML forecasting)
- ✅ IAM permissions: `roles/bigquery.dataViewer` + `roles/bigquery.jobUser`

### 2. Access the Agent

Open **http://127.0.0.1:8000** and select **finops-cost-data-analyst**.

### 3. Try Example Queries

Start with these simple queries:

**A. SQL-Based (Level 1)**:
```
"Show me the top 5 most expensive applications in February 2025"
```

**B. ML Forecasting (Level 2A)**:
```
"Forecast total costs for next 7 days"
```

**C. AI Insights (Level 2B)**:
```
"What patterns do you see in my cost data?"
```

### 4. Verify AI Features Work

Check agent logs for:
```
[sql_generation] Using tool: forecast
[sql_generation] Using tool: ask_data_insights
```

If you see these, ML features are working!

---

## 📊 Performance Tips

### For Best ML Forecasting Results

1. **Data Volume**:
   - Minimum: 30 days of historical data
   - Recommended: 90+ days for accurate trends
   - Ideal: 1+ year for seasonality detection

2. **Data Granularity**:
   - Daily aggregations work best for short-term forecasts (7-30 days)
   - Weekly aggregations for medium-term (1-3 months)
   - Monthly aggregations for long-term (3-12 months)

3. **Table Partitioning**:
   - Partition cost tables by `date` column
   - Reduces query costs for ML forecasting
   - Improves performance on large datasets

4. **Query Optimization**:
   - Be specific about time ranges ("next 14 days" vs "future costs")
   - Specify applications/services for focused forecasts
   - Use confidence intervals for uncertainty quantification

---

## 🔒 Security & Compliance

### Data Privacy

- **Read-Only**: All operations are read-only (`WriteMode.BLOCKED`)
- **No Data Modification**: Agent cannot INSERT, UPDATE, or DELETE data
- **Audit Logging**: All BigQuery queries are logged in Cloud Audit Logs

### Cost Control

- **Query Cost Estimation**: BigQuery AI functions may have additional costs
- **Forecast Limits**: Recommend limiting forecast horizon to 90 days
- **Quota Management**: Monitor BigQuery job quotas

### Best Practices

1. **Start Small**: Test on small datasets first
2. **Monitor Costs**: Check BigQuery billing for ML function costs
3. **Set Budgets**: Use GCP budget alerts for BigQuery spending
4. **Review Queries**: Check generated SQL before running on large datasets

---

## 🐛 Troubleshooting

### "ML.FORECAST not found"

**Cause**: BigQuery ML is not enabled in your project
**Fix**: Run `bq query "SELECT 1"` to enable BigQuery API

### "Insufficient data for forecasting"

**Cause**: Less than 30 days of historical data
**Fix**: Load more historical cost data or use SQL-based anomaly detection

### "ask_data_insights quota exceeded"

**Cause**: Free tier limits on Gemini API calls
**Fix**:
1. Wait 60 seconds for quota reset
2. Switch to `gemini-1.5-flash` (higher quota)
3. Upgrade to paid tier

### "Permission denied on ML.FORECAST"

**Cause**: Service account missing BigQuery permissions
**Fix**: Grant `roles/bigquery.jobUser` to your service account

---

## 📚 References

### BigQuery AI Documentation

- [BigQuery ML Forecasting](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-forecast)
- [BigQuery AI Insights](https://cloud.google.com/bigquery/docs/ask-data-insights)
- [Time Series Forecasting Tutorial](https://cloud.google.com/bigquery/docs/arima-tutorial)

### Agent Documentation

- [README.md](./README.md) - User guide
- [MIGRATION.md](./MIGRATION.md) - Setup guide
- [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) - Architecture details
- [CLAUDE.md](./CLAUDE.md) - Developer guide

---

## 🎉 Summary

**What You Can Now Do**:

✅ Detect cost anomalies using SQL analytics (Level 1)
✅ Forecast future costs with ML models (Level 2A)
✅ Get AI-generated insights about cost patterns (Level 2B)
✅ Combine SQL + ML for advanced anomaly detection
✅ Multi-table analysis (cost, budget, usage)
✅ Natural language queries for complex analysis

**Next Steps**:

1. Open **http://127.0.0.1:8000**
2. Select **finops-cost-data-analyst** agent
3. Try example queries above
4. Monitor logs for ML function calls
5. Experiment with forecasting horizons and insights

---

**Status**: 🚀 **READY FOR ANOMALY DETECTION**

**Version**: 2.1 - ML-Based Anomaly Detection
**Prepared By**: Claude Code
**Date**: October 22, 2025
