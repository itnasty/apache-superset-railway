# Apache Superset Performance Optimization Guide

## Current Setup Analysis

### What We Have Now
- **Redis Caching**: 4 cache layers (Results, Data, Filter State, Explore Form)
- **Synchronous Loading**: Charts load sequentially (Railway limitation)
- **24-hour TTL**: Default cache retention
- **Basic Configuration**: Minimal optimization

### Current Bottlenecks
1. **Sequential chart loading** (CONCURRENT_CHART_LOAD_LIMIT=1)
2. **No query result preloading**
3. **No thumbnail caching**
4. **Default cache timeouts**
5. **No cache warming**

## Performance Optimization Strategies

### 1. Advanced Redis Caching Configuration

#### A. Thumbnail Cache (Visual Performance)
```python
# Add to superset_config.py
THUMBNAIL_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 604800,  # 7 days for thumbnails
    "CACHE_KEY_PREFIX": "superset_thumb_",
    "CACHE_REDIS_HOST": redis_parsed.hostname,
    "CACHE_REDIS_PORT": redis_parsed.port or 6379,
    "CACHE_REDIS_PASSWORD": redis_parsed.password,
    "CACHE_REDIS_DB": 4,
}

# Enable thumbnail generation
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
}

THUMBNAIL_SELENIUM_USER = "admin"  # User for generating thumbnails
```

#### B. Metadata Cache (Schema/Table Info)
```python
METADATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
    "CACHE_KEY_PREFIX": "superset_meta_",
    "CACHE_REDIS_HOST": redis_parsed.hostname,
    "CACHE_REDIS_PORT": redis_parsed.port or 6379,
    "CACHE_REDIS_PASSWORD": redis_parsed.password,
    "CACHE_REDIS_DB": 5,
}
```

#### C. Optimized Cache Timeouts
```python
# Different TTLs for different cache types
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes for general cache
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": REDIS_URL,
}

# Specific timeouts
RESULTS_BACKEND_CACHE_TIMEOUT = 3600  # 1 hour for query results
DATA_CACHE_TIMEOUT = 86400  # 24 hours for data
FILTER_STATE_CACHE_TIMEOUT = 86400  # 24 hours for filters
EXPLORE_FORM_DATA_CACHE_TIMEOUT = 7200  # 2 hours for explore
```

### 2. Database Query Optimization

#### A. Connection Pooling
```python
# Optimize database connections
SQLALCHEMY_POOL_SIZE = 20  # Increase pool size
SQLALCHEMY_POOL_RECYCLE = 3600  # Recycle connections every hour
SQLALCHEMY_MAX_OVERFLOW = 40  # Allow more overflow connections
```

#### B. Query Limits
```python
# Optimize query performance
ROW_LIMIT = 10000  # Reduce from 50000 for faster queries
SAMPLES_ROW_LIMIT = 1000  # Limit sample queries
SQL_MAX_ROW = 100000  # Maximum rows for SQL Lab
```

### 3. Cache Warming Strategies

#### A. Scheduled Cache Warming
```python
# Create a cache warming script (cache_warmer.py)
import requests
import json
from datetime import datetime

def warm_dashboard_cache(dashboard_id, base_url):
    """Pre-load dashboard data into cache"""
    
    # List of common filters/parameters
    filters = [
        {"date_range": "last_7_days"},
        {"date_range": "last_30_days"},
        {"date_range": "last_quarter"},
    ]
    
    for filter_set in filters:
        # Trigger dashboard load with different filters
        url = f"{base_url}/api/v1/dashboard/{dashboard_id}/data"
        requests.post(url, json=filter_set)
        
def warm_critical_dashboards():
    """Warm cache for frequently accessed dashboards"""
    critical_dashboards = [1, 2, 3]  # Your dashboard IDs
    
    for dash_id in critical_dashboards:
        warm_dashboard_cache(dash_id, "https://your-superset-url")
```

#### B. Automated Cache Warming (Cron Job)
```bash
# Add to your deployment
0 6 * * * python /app/cache_warmer.py  # Run daily at 6 AM
*/30 * * * * python /app/cache_warmer.py --critical-only  # Every 30 min for critical
```

### 4. Frontend Optimization

#### A. Enable Compression
```python
# Enable gzip compression
COMPRESS_REGISTER = True
COMPRESS_MIN_SIZE = 500  # Minimum size to compress

# Static file caching
SEND_FILE_MAX_AGE_DEFAULT = 604800  # 7 days for static files
```

#### B. Dashboard Performance Features
```python
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_VIRTUALIZATION": True,  # Virtual scrolling for large dashboards
    "DASHBOARD_NATIVE_FILTERS": True,  # Faster native filters
    "DASHBOARD_CROSS_FILTERS": True,  # Cross-filtering between charts
    "ENABLE_EXPLORE_DRAG_AND_DROP": True,
    "DISABLE_LEGACY_DATASOURCE_EDITOR": True,
}
```

### 5. Railway-Specific Optimizations

#### A. Gradual Concurrent Loading
```python
# Carefully increase concurrent loading (test incrementally)
CONCURRENT_CHART_LOAD_LIMIT = 2  # Try 2 instead of 1
DASHBOARD_VIRTUALIZATION_LIMIT = 10  # Render 10 charts at once
```

#### B. Resource Optimization
```python
# Memory management
CACHE_REDIS_MAX_CONNECTIONS = 50  # Connection pool for Redis
WTF_CSRF_ENABLED = False  # Already disabled
ENABLE_PROXY_FIX = True  # Already enabled

# Timeouts balanced for Railway
SUPERSET_WEBSERVER_TIMEOUT = 900  # 15 minutes
SQLLAB_ASYNC_TIME_LIMIT_SEC = 900
SQLLAB_TIMEOUT = 900
```

### 6. Monitoring & Metrics

#### A. Performance Tracking
```python
# Enable stats logging
STATS_LOGGER = True
EVENT_LOGGER = True

# StatsD configuration (if using DataDog/similar)
STATSD_HOST = 'localhost'
STATSD_PORT = 8125
STATSD_PREFIX = 'superset'
```

#### B. Cache Hit Rate Monitoring
```python
# Add to your monitoring script
def check_cache_performance():
    """Monitor cache hit rates"""
    import redis
    
    r = redis.from_url(REDIS_URL)
    info = r.info('stats')
    
    hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
    print(f"Cache hit rate: {hit_rate:.2%}")
    
    # Alert if hit rate < 70%
    if hit_rate < 0.7:
        send_alert("Low cache hit rate")
```

### 7. Advanced Query Optimization

#### A. Materialized Views
```sql
-- Create materialized views for complex queries
CREATE MATERIALIZED VIEW dashboard_summary AS
SELECT 
    date_trunc('day', created_at) as day,
    COUNT(*) as count,
    SUM(amount) as total
FROM transactions
GROUP BY 1;

-- Refresh periodically
CREATE INDEX idx_dashboard_summary_day ON dashboard_summary(day);
```

#### B. Query Result Caching Strategy
```python
# Force cache for expensive queries
QUERY_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 3600,
    "CACHE_KEY_PREFIX": "query_",
    "CACHE_REDIS_URL": REDIS_URL,
}

# Cache key includes user context
CACHE_KEY_FACTORY = lambda: f"{current_user.id}_{request.url}"
```

### 8. Deployment Optimization

#### A. Multi-Service Architecture
```yaml
# Consider splitting services on Railway
services:
  - superset-web:  # Frontend only
      replicas: 2
  - superset-worker:  # Background jobs
      replicas: 1
  - redis:  # Already have
  - postgres:  # Already have
```

#### B. CDN for Static Assets
```python
# Use CDN for static files
STATIC_ASSET_CDN = "https://cdn.jsdelivr.net/npm/@superset-ui/"
FAVICONS = [{"href": "https://your-cdn.com/favicon.ico"}]
```

## Implementation Priority

### Phase 1: Quick Wins (Immediate)
1. ✅ Redis caching (DONE)
2. Increase cache timeouts
3. Enable compression
4. Add thumbnail cache

### Phase 2: Medium Effort (This Week)
1. Implement cache warming
2. Add monitoring
3. Optimize database queries
4. Enable dashboard virtualization

### Phase 3: Advanced (Next Month)
1. Materialized views
2. Multi-service architecture
3. CDN integration
4. Custom cache strategies

## Performance Metrics to Track

1. **Cache Hit Rate**: Target > 80%
2. **Dashboard Load Time**: Target < 3 seconds
3. **Query Response Time**: Target < 2 seconds
4. **Time to First Chart**: Target < 1 second
5. **Redis Memory Usage**: Monitor < 80% capacity

## Testing Performance Improvements

```python
# Performance test script
import time
import requests

def test_dashboard_performance(dashboard_id):
    """Measure dashboard load time"""
    
    # Cold cache
    start = time.time()
    response1 = requests.get(f"/api/v1/dashboard/{dashboard_id}")
    cold_time = time.time() - start
    
    # Warm cache
    start = time.time()
    response2 = requests.get(f"/api/v1/dashboard/{dashboard_id}")
    warm_time = time.time() - start
    
    improvement = (cold_time - warm_time) / cold_time * 100
    print(f"Cold: {cold_time:.2f}s, Warm: {warm_time:.2f}s")
    print(f"Cache improvement: {improvement:.1f}%")
```

## Troubleshooting

### If Performance Degrades:
1. Check Redis memory: `redis-cli INFO memory`
2. Monitor slow queries: Enable `SQLLAB_QUERY_COST_ESTIMATE`
3. Review cache hit rates
4. Check Railway metrics for throttling
5. Analyze browser network tab for slow requests

### Common Issues:
- **High memory usage**: Reduce cache TTLs
- **Slow queries**: Add database indexes
- **Cache misses**: Implement cache warming
- **Network latency**: Use internal Railway URLs

## Next Steps

1. Implement Phase 1 optimizations
2. Set up monitoring dashboard
3. Benchmark current vs. optimized performance
4. Document specific query optimizations
5. Create cache warming schedule