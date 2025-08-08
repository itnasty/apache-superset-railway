# RAILWAY_DEPLOYMENT_GUIDE.md

## Emergency Fix for Dashboard Network Errors

This guide addresses the "Unexpected error" issues when loading dashboards in Apache Superset deployed on Railway.

### 🚨 CRITICAL CHANGES MADE

1. **DISABLED Async Queries**:
   - `GLOBAL_ASYNC_QUERIES`: TRUE → **FALSE**
   - `SUPERSET_LOAD_CHART_ASYNC`: TRUE → **FALSE**
   - This forces synchronous chart loading

2. **Sequential Chart Loading**:
   - `CONCURRENT_CHART_LOAD_LIMIT`: 8 → **1**
   - Charts now load one at a time to prevent overload

3. **Maximized Timeouts**:
   - `WEB_QUERY_TIMEOUT`: 600 → **900** seconds (15 min)
   - `DATABASE_QUERY_TIMEOUT`: 120 → **300** seconds (5 min)
   - `SUPERSET_WEBSERVER_TIMEOUT`: 600 → **900** seconds

4. **Simplified Server**:
   - Removed Gunicorn/gevent
   - Using development server with threads
   - More stable for Railway's infrastructure

5. **CORS Fully Opened**:
   - All origins allowed (`*`)
   - All methods allowed
   - All headers exposed

6. **CSRF Protection Relaxed**:
   - Added exemptions for all dashboard/chart endpoints
   - Disabled CSRF time limits

### Railway Environment Variables

**REQUIRED** - Set these in Railway:

```bash
# Admin credentials
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=<secure-password>
SECRET_KEY=<generate-a-secure-32-char-key>

# Database (Railway auto-provides DATABASE)
# For external database:
DATABASE_URL=postgresql://user:pass@host:port/dbname

# IMPORTANT: Force synchronous mode
GLOBAL_ASYNC_QUERIES=false
SUPERSET_LOAD_CHART_ASYNC=false
CONCURRENT_CHART_LOAD_LIMIT=1

# Extended timeouts
WEB_QUERY_TIMEOUT=900
DATABASE_QUERY_TIMEOUT=300
SUPERSET_WEBSERVER_TIMEOUT=900
```

### Immediate Actions After Deployment

1. **Wait for Deployment**:
   ```bash
   railway logs -n 100
   ```
   Look for: "✅ Superset initialization complete!"

2. **Clear Everything**:
   - Clear browser cache (Ctrl+Shift+Del)
   - Clear cookies for your Railway domain
   - Use incognito/private mode for testing

3. **Test Gradually**:
   - First: Test login
   - Second: Test individual charts
   - Third: Test simple dashboard (1-2 charts)
   - Fourth: Test complex dashboards

### Diagnostic Steps

1. **Run Diagnostic Script**:
   ```bash
   railway run python diagnose_dashboard_issues.py
   ```

2. **Check Browser Console** (F12):
   - Network tab: Look for failed requests
   - Console tab: Look for JavaScript errors
   - Check for CORS errors

3. **Monitor Railway Logs**:
   ```bash
   # Watch for errors
   railway logs -f | grep -E "(ERROR|CRITICAL|Failed)"
   
   # Check memory usage
   railway logs | grep -i memory
   ```

### If Still Not Working

1. **Database Connection Pool**:
   ```bash
   # Add to Railway env vars
   SQLALCHEMY_POOL_SIZE=5
   SQLALCHEMY_MAX_OVERFLOW=0
   ```

2. **Enable Debug Mode**:
   ```bash
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

3. **Try Even More Conservative Settings**:
   ```bash
   # Reduce limits further
   ROW_LIMIT=1000
   VIZ_ROW_LIMIT=500
   SQL_MAX_ROW=5000
   ```

4. **Add Redis** (if possible):
   - Deploy Redis on Railway
   - Add `REDIS_URL` to environment

### Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| "Network Error" | Timeout or CORS | Check timeouts, clear cache |
| "Unexpected Error" | Async query failure | Ensure async is disabled |
| "504 Gateway Timeout" | Railway proxy timeout | Reduce query complexity |
| "Connection Reset" | Too many concurrent requests | Ensure CONCURRENT_CHART_LOAD_LIMIT=1 |

### Nuclear Option

If nothing works, try this minimal config:

```bash
# In Railway env vars
FEATURE_FLAGS='{"GLOBAL_ASYNC_QUERIES":false,"DASHBOARD_VIRTUALIZATION":false,"DASHBOARD_CACHE":false}'
WTF_CSRF_ENABLED=false
ENABLE_CORS=true
COMPRESS_ENABLED=false
```

### Getting Help

1. **Check Specific Errors**:
   - Railway logs: `railway logs -n 500`
   - Browser console errors
   - Network tab failed requests

2. **Share Diagnostics**:
   - Run diagnostic script output
   - Specific error messages
   - Browser console screenshots

The key insight is that Railway's infrastructure seems to have issues with:
- Async/concurrent requests
- WebSocket connections
- Complex proxy configurations

By forcing everything to be synchronous and sequential, we work around these limitations.
