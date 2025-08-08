# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Apache Superset deployment template optimized for Railway platform. It packages Apache Superset with critical fixes for dashboard loading issues specific to Railway's infrastructure constraints.

**Railway Service Name**: `apache-superset`

## Essential Commands

### Local Development
```bash
# Build Docker image locally
docker build -t superset-railway .

# Run locally with environment variables
docker run -p 8088:8088 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_EMAIL=admin@example.com \
  -e ADMIN_PASSWORD=admin \
  -e SECRET_KEY=ThisIsNotSecure123 \
  superset-railway

# View logs
docker logs -f <container-id>
```

### Railway Deployment
```bash
# Deploy to Railway (service name: apache-superset)
railway up

# View deployment logs for apache-superset service
railway logs -n 100

# Run diagnostic script in apache-superset service
railway run python diagnose_dashboard_issues.py

# Monitor errors in apache-superset logs
railway logs -f | grep -E "(ERROR|CRITICAL|Failed)"
```

## Architecture & Key Components

### Core Files Structure
- **Dockerfile**: Builds from `apache/superset:latest`, installs database drivers and custom configuration
- **config/superset_config.py**: Critical Superset configuration with Railway-specific optimizations
- **config/superset_init.sh**: Initialization script that handles database setup, admin user creation, and server startup
- **requirements.txt**: Additional Python dependencies for database drivers and Redis support
- **railway.json**: Railway deployment configuration

### Critical Configuration Decisions

1. **Synchronous Operation Only**: All async operations are disabled (`GLOBAL_ASYNC_QUERIES=false`) due to Railway infrastructure limitations
2. **Sequential Chart Loading**: Charts load one at a time (`CONCURRENT_CHART_LOAD_LIMIT=1`) to prevent overload
3. **Extended Timeouts**: All timeouts set to 15 minutes to handle Railway's proxy behavior
4. **Development Server**: Uses Flask development server instead of Gunicorn for stability on Railway

### Environment Variables (Required)
```bash
ADMIN_USERNAME      # Admin user for Superset
ADMIN_EMAIL         # Admin email
ADMIN_PASSWORD      # Admin password
SECRET_KEY          # Session encryption key (auto-generated if not set)
DATABASE            # Database URL (auto-provided by Railway)

# Performance settings (MUST be set on Railway)
GLOBAL_ASYNC_QUERIES=false
SUPERSET_LOAD_CHART_ASYNC=false
CONCURRENT_CHART_LOAD_LIMIT=1
WEB_QUERY_TIMEOUT=900
DATABASE_QUERY_TIMEOUT=300
```

## Critical Implementation Notes

### Dashboard Loading Issues
The main challenge is Railway's infrastructure doesn't handle async/concurrent requests well. The solution:
- Force all queries to run synchronously
- Load charts sequentially, not in parallel
- Maximize all timeout values
- Disable CSRF for chart/dashboard endpoints

### Database Initialization Flow
1. `superset db upgrade` - Migrates database schema
2. `superset fab create-admin` - Creates admin user if not exists
3. `superset init` - Initializes Superset roles and permissions
4. Server starts on port from `$PORT` environment variable (Railway provides this)

### Common Issues and Solutions

**Dashboard shows "Unexpected error"**:
- Verify async settings are disabled in environment variables
- Clear browser cache and cookies
- Check Railway logs for timeout errors

**504 Gateway Timeout**:
- Reduce query complexity
- Ensure timeout environment variables are set
- Consider adding Redis for caching

**Database connection issues**:
- Railway provides `DATABASE` env var automatically for Postgres
- For external databases, use `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`

## Testing Changes

When modifying configuration:
1. Test locally with Docker first
2. Deploy to Railway staging environment
3. Clear browser cache before testing
4. Start with simple dashboards (1-2 charts) before complex ones
5. Monitor Railway logs during dashboard loading

## Railway-Specific Constraints

- No WebSocket support (affects real-time features)
- Proxy timeout at 30 seconds (handled by our extended timeouts)
- Limited concurrent connections (handled by sequential loading)
- No persistent file storage (use database or external storage)