# RAILWAY_DEPLOYMENT_GUIDE.md

## Fix for Dashboard Network Errors

This guide addresses the "Unexpected error" issues when loading dashboards in Apache Superset deployed on Railway.

### Changes Made

1. **Increased Timeouts**:
   - `WEB_QUERY_TIMEOUT`: 300 → 600 seconds
   - `DATABASE_QUERY_TIMEOUT`: 60 → 120 seconds
   - `SUPERSET_WEBSERVER_TIMEOUT`: 300 → 600 seconds
   - Added `SQLLAB_TIMEOUT`: 600 seconds
   - Added `GUNICORN_TIMEOUT`: 600 seconds

2. **Improved CORS Configuration**:
   - Added proper CORS headers including `expose_headers` for CSRFToken
   - Added all HTTP methods to CORS allowed methods
   - Added CSRF exemptions for dashboard and chart data endpoints

3. **Session Cookie Fixes**:
   - Changed `SESSION_COOKIE_SAMESITE` from "None" to "Lax"
   - Changed `SESSION_COOKIE_SECURE` to "True" for HTTPS
   - Changed `SESSION_COOKIE_HTTPONLY` to "True" for security

4. **Async Query Configuration**:
   - Kept async queries enabled for better performance
   - Added `GLOBAL_ASYNC_QUERIES_POLLING_DELAY`: 500ms
   - Increased `CONCURRENT_CHART_LOAD_LIMIT` from 4 to 8

5. **Proxy Configuration**:
   - Added proper proxy fix configuration for Railway's reverse proxy
   - Added Railway domain detection in startup script

6. **Performance Improvements**:
   - Added Gunicorn with gevent workers for better concurrency
   - Added chart caching configuration
   - Added compression support

### Railway Environment Variables

Set these environment variables in your Railway project:

```bash
# Required
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=<secure-password>
SECRET_KEY=<generate-a-secure-key>

# Database (Railway provides DATABASE automatically)
# If using external database:
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Performance (optional but recommended)
USE_GUNICORN=true
GUNICORN_WORKERS=2
GUNICORN_WORKER_CLASS=gevent

# Redis for caching (optional but recommended)
REDIS_URL=redis://...

# Increase limits if needed
WEB_QUERY_TIMEOUT=600
DATABASE_QUERY_TIMEOUT=120
SUPERSET_WEBSERVER_TIMEOUT=600
CONCURRENT_CHART_LOAD_LIMIT=8
```

### Deployment Steps

1. **Deploy the Updated Code**:
   - Railway will automatically detect the changes and redeploy

2. **Monitor Logs**:
   ```bash
   railway logs
   ```

3. **Clear Browser Cache**:
   - Clear your browser cache and cookies for your Superset domain
   - This ensures the new session cookie settings take effect

4. **Test Dashboard Loading**:
   - Start with simple dashboards first
   - Gradually test more complex dashboards

### Troubleshooting

If you still experience issues:

1. **Check Browser Console**:
   - Open Developer Tools (F12)
   - Look for CORS errors or failed requests
   - Check the Network tab for timeout errors

2. **Check Railway Logs**:
   ```bash
   railway logs | grep -i error
   ```

3. **Verify Environment Variables**:
   - Ensure all required variables are set in Railway
   - Check that `RAILWAY_PUBLIC_DOMAIN` is automatically set

4. **Database Connection**:
   - Ensure your database has sufficient connections available
   - Consider using a connection pooler if using PostgreSQL

5. **Redis Connection** (if using):
   - Verify Redis is accessible
   - Check Redis memory usage

### Additional Optimizations

If you continue to experience issues:

1. **Enable Dashboard Virtualization**:
   ```bash
   DASHBOARD_VIRTUALIZATION=true
   ```

2. **Reduce Chart Complexity**:
   - Simplify complex queries
   - Add proper indexes to your database
   - Use materialized views for heavy aggregations

3. **Scale Railway Resources**:
   - Consider upgrading your Railway plan for more resources
   - Add more replicas if on a paid plan

### Support

If issues persist after these changes:
1. Check Superset logs for specific error messages
2. Review your database query performance
3. Consider implementing a CDN for static assets
