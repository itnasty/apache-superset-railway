#!/bin/bash
set -e

echo "Starting Superset with optimized configuration..."

# Database setup
superset db upgrade || echo "DB upgrade failed, continuing..."

# Create or update admin user
echo "Setting up admin user..."
if superset fab create-admin \
    --username "${ADMIN_USERNAME:-admin}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL:-admin@example.com}" \
    --password "${ADMIN_PASSWORD:-admin}"; then
    echo "✅ Admin user created successfully"
else
    echo "⚠️  Admin user already exists, resetting password..."
    superset fab reset-password --username "${ADMIN_USERNAME:-admin}" --password "${ADMIN_PASSWORD:-admin}"
    echo "✅ Admin password reset successfully"
fi

# Initialize Superset
superset init || echo "Init failed, continuing..."

# Apply cache timeout patch
echo "🔧 Applying cache timeout patch..."
python /app/apply_patch.py || echo "⚠️ Patch application failed, continuing..."

# Cache warming (simplified - no cron due to permissions)
if [ "${ENABLE_CACHE_WARMING:-true}" = "true" ]; then
    echo "🔄 Scheduling initial cache warming..."
    
    # Create log directory in app directory (writable)
    mkdir -p /app/logs
    
    # Run initial cache warming in background after 90 seconds
    # Try enhanced warmer first, fallback to basic if not available
    (sleep 90 && \
     if [ -f /app/scripts/cache_warmer_enhanced.py ]; then \
         python /app/scripts/cache_warmer_enhanced.py --url http://localhost:${PORT:-8088} --dashboard-ids 1,2,3,4,5 > /app/logs/cache_warmer.log 2>&1; \
     else \
         python /app/scripts/cache_warmer.py --url http://localhost:${PORT:-8088} --critical-only > /app/logs/cache_warmer.log 2>&1; \
     fi || true) &
    echo "✅ Cache warming will start in 90 seconds..."
fi

# Log Redis connection status
if [ -n "$REDIS_URL" ]; then
    echo "✅ Redis caching enabled: 6 cache layers active"
    echo "   - Query Results Cache (1hr TTL)"
    echo "   - Dashboard Data Cache (24hr TTL)"
    echo "   - Filter State Cache (24hr TTL)"
    echo "   - Explore Form Cache (2hr TTL)"
    echo "   - Thumbnail Cache (7d TTL)"
    echo "   - Metadata Cache (24hr TTL)"
else
    echo "⚠️  Redis not configured - running without caching"
fi

# Start the server with Gunicorn (production mode)
echo "Starting Superset server with Gunicorn on port ${PORT:-8088}..."
echo "🚀 Production mode enabled with Gunicorn + Gevent workers"
echo "Workers: ${WEB_CONCURRENCY:-2}, Threads: ${GUNICORN_THREADS:-8}, Timeout: ${GUNICORN_TIMEOUT:-120}s"

# Use Gunicorn for production deployment
exec gunicorn "superset.app:create_app()" --config /app/gunicorn_config.py
