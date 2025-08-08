# High Volume Sales Data Optimization Guide

## Current Challenge
You have high sales data volume that might exceed the current 10K row limit, potentially truncating important data in dashboards.

## Recommended Approach

### Option 1: Smart Limits (Recommended) ✅
Keep moderate limits but use data strategies:

```python
ROW_LIMIT = 25000  # Balanced for performance
```

**Pros:**
- 2-3x more data than current
- Still fast (3-5 seconds)
- Cache remains efficient
- No timeout risks

**Cons:**
- May still truncate very large datasets
- Not suitable for raw transaction-level data

### Option 2: Increase Limits (With Caution) ⚠️
```python
ROW_LIMIT = 50000  # or even 100000
```

**Pros:**
- More complete data
- Less truncation

**Cons:**
- 5-10x slower queries
- Larger memory usage
- Risk of timeouts
- Bigger cache (costs more Redis memory)

## Best Practices for High Volume Sales Data

### 1. **Use Aggregated Tables** 🎯
Instead of querying millions of raw sales records, create summary tables:

```sql
-- Create daily sales summary
CREATE MATERIALIZED VIEW sales_summary_daily AS
SELECT 
    DATE(sale_date) as day,
    product_category,
    region,
    SUM(amount) as total_sales,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_sale
FROM sales_transactions
GROUP BY DATE(sale_date), product_category, region;

-- Refresh nightly
CREATE INDEX idx_sales_summary_day ON sales_summary_daily(day);
```

**Result:** Query 365 rows instead of 1M+ rows for yearly view

### 2. **Implement Time-Window Defaults** ⏰
Don't load all historical data by default:

```python
# In your dataset configuration
{
    "time_range_endpoints": ["inclusive", "exclusive"],
    "time_columns": {
        "columns": ["sale_date"],
        "default_time_range": "Last 90 days"  # Don't load 5 years by default
    }
}
```

### 3. **Use Filters Effectively** 🔍
Pre-filter data at the database level:

```sql
-- Bad: Load all data then filter in Superset
SELECT * FROM sales;

-- Good: Filter at database
SELECT * FROM sales 
WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days'
AND region = '{{ current_user_region }}';
```

### 4. **Optimize Your Charts** 📊

| Chart Type | Good for | Row Limit Needed |
|------------|----------|------------------|
| Time Series | Trends | 365-1000 (daily) |
| Pie Chart | Categories | 10-20 |
| Bar Chart | Comparisons | 20-100 |
| Table | Details | 100-1000 |
| Big Number | KPIs | 1 |
| Heatmap | Patterns | 1000-5000 |

### 5. **Cache Strategy for Large Data** 💾

```python
# Different cache TTLs for different data types
if "summary" in query:
    cache_timeout = 86400  # 24 hours for summaries
elif "realtime" in query:
    cache_timeout = 300  # 5 minutes for real-time
else:
    cache_timeout = 3600  # 1 hour default
```

### 6. **Progressive Loading Pattern** 📈

Create multiple dashboards:
1. **Executive Summary** - Highly aggregated (loads fast)
2. **Department View** - Moderate detail
3. **Analyst Deep Dive** - Full detail (slower, for power users)

## Implementation Steps

### To Apply High-Volume Configuration:

1. **Test locally first:**
```bash
# Back up current config
cp config/superset_config.py config/superset_config_backup.py

# Apply high-volume config
cp config/superset_config_highvolume.py config/superset_config.py
```

2. **Create aggregated tables in your database:**
```sql
-- Run these in your PostgreSQL
CREATE MATERIALIZED VIEW sales_hourly AS ...;
CREATE MATERIALIZED VIEW sales_daily AS ...;
CREATE MATERIALIZED VIEW sales_weekly AS ...;
CREATE MATERIALIZED VIEW sales_monthly AS ...;
```

3. **Update your dashboards:**
- Point charts to aggregated views
- Add time range filters
- Set appropriate row limits per chart

4. **Deploy and monitor:**
```bash
git add -A
git commit -m "Optimize for high-volume sales data"
git push
```

## Monitoring Performance

Check query performance:
```sql
-- In Superset SQL Lab
EXPLAIN ANALYZE 
SELECT * FROM your_sales_query;
```

Monitor cache effectiveness:
```python
# Run periodically
python check_redis_data.py
```

## Decision Matrix

| Your Data Volume | Recommended ROW_LIMIT | Strategy |
|-----------------|----------------------|----------|
| < 10K daily records | 10000 (current) | Keep as is |
| 10K-50K daily | 25000 | Use smart limits |
| 50K-200K daily | 25000 + aggregations | Aggregate tables |
| 200K+ daily | 10000 + aggregations | Heavy aggregation |
| Millions daily | 5000 + data warehouse | Consider dedicated OLAP |

## Quick Wins for Immediate Improvement

1. **Create a "Last 30 Days" default filter** - Reduces data 12x for yearly dashboards
2. **Add a daily summary table** - Query 30 rows instead of 300K
3. **Cache your top 5 dashboards** - Already implemented!
4. **Use Big Number charts for KPIs** - Only needs 1 row each

## Need Help Deciding?

Answer these questions:
1. How many sales records per day? _______
2. How far back do users typically look? _______
3. Do users need transaction-level detail? Y/N
4. Are dashboards slow currently? Y/N

Based on your answers:
- If < 50K daily + last 90 days → Increase to 25K limit
- If > 50K daily → Keep 10K + implement aggregations
- If transaction detail needed → Create drill-down dashboards
- If currently slow → Focus on aggregations first