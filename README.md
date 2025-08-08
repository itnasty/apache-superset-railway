# Apache Superset for Railway 🚀

<img src="./logo.png" alt="Superset" width="500"/>

Run [Apache Superset](https://superset.apache.org/) on [Railway](https://railway.app/) with one click!

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/zJvWRH?referralCode=ySCncj)

## 🚨 IMPORTANT: Dashboard Network Error Fix Applied

This repository includes critical fixes for dashboard loading issues on Railway. Key changes:
- **Async queries DISABLED** - Forces synchronous chart loading
- **Sequential chart loading** - Charts load one at a time
- **Extended timeouts** - 15-minute timeouts for complex queries
- **Simplified server** - Uses development server for stability

## Features ✨

- 📊 Modern data exploration and visualization platform
- 🔧 Pre-configured for Railway deployment
- 🗄️ Supports PostgreSQL, MySQL, and SQLite databases
- 🚀 Production-ready configuration
- 🔐 Secure by default with customizable admin credentials

## Quick Start 🏁

1. Click the "Deploy on Railway" button above
2. Configure environment variables:
   - `ADMIN_USERNAME` - Admin username (required)
   - `ADMIN_EMAIL` - Admin email (required)
   - `ADMIN_PASSWORD` - Admin password (required)
   - `SECRET_KEY` - Secret key for session encryption (auto-generated if not provided)
   - `DATABASE` - Database URL (auto-provided by Railway)

3. Deploy and wait for the build to complete
4. Access your Superset instance at the provided Railway URL

## Environment Variables 🔧

### Required Variables
- `ADMIN_USERNAME` - Admin user username
- `ADMIN_EMAIL` - Admin user email
- `ADMIN_PASSWORD` - Admin user password

### Critical Performance Variables (Set These!)
```bash
# Force synchronous mode (REQUIRED for Railway)
GLOBAL_ASYNC_QUERIES=false
SUPERSET_LOAD_CHART_ASYNC=false
CONCURRENT_CHART_LOAD_LIMIT=1

# Extended timeouts
WEB_QUERY_TIMEOUT=900
DATABASE_QUERY_TIMEOUT=300
SUPERSET_WEBSERVER_TIMEOUT=900
```

### Optional Variables
- `SECRET_KEY` - Session encryption key (auto-generated if not set)
- `DATABASE` or `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis URL for caching (optional but recommended)
- `MAPBOX_API_KEY` - For map visualizations

## Troubleshooting Dashboard Errors 🔍

If you see "Unexpected error" in dashboards:

1. **Clear browser cache and cookies**
2. **Verify environment variables are set** (especially the async settings)
3. **Run diagnostic script**:
   ```bash
   railway run python diagnose_dashboard_issues.py
   ```
4. **Check logs**:
   ```bash
   railway logs -n 100
   ```

See [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

## Database Support 💾

This template supports:
- PostgreSQL (recommended for production)
- MySQL/MariaDB
- SQLite (default fallback)
- Any database supported by SQLAlchemy

## Configuration 🛠️

The Superset configuration is optimized for Railway deployment with:
- Proper CORS headers for API access
- Session cookie configuration for HTTPS
- Extended timeouts for complex queries
- Disabled async queries for stability
- Health check endpoint at `/health`

## Support 🤝

- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Railway Documentation](https://docs.railway.app/)
- [Report Issues](https://github.com/itnasty/apache-superset-railway/issues)

## License 📄

Apache Superset is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/apache/superset/blob/master/LICENSE.txt) file for details.
