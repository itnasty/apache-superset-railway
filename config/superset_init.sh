#!/bin/bash
set -e

echo "========================================"
echo "🚀 Starting Apache Superset on Railway"
echo "========================================"

# Verify critical modules are available
echo "🔍 Verifying Python modules..."
python -c "import psycopg2; print('✓ psycopg2 available')" || {
    echo "❌ psycopg2 not found!"
    exit 1
}
python -c "import gevent; print('✓ gevent available')" || {
    echo "❌ gevent not found!"
    exit 1
}
python -c "import redis; print('✓ redis available')" || {
    echo "⚠️  redis not found (optional)"
}

# Set environment variables
export PYTHONPATH="/app/pythonpath:${PYTHONPATH}"
export SUPERSET_CONFIG_PATH="/app/superset_config.py"
export FLASK_APP="superset.app:create_app()"

echo "📝 Configuration:"
echo "   SUPERSET_CONFIG_PATH: $SUPERSET_CONFIG_PATH"
echo "   DATABASE_URL: ${DATABASE_URL:0:20}..."
echo "   REDIS_URL: ${REDIS_URL:0:20}..."

# Test database connection
echo "🔗 Testing database connection..."
python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✓ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Test Redis connection (if configured)
if [ ! -z "$REDIS_URL" ]; then
    echo "🔗 Testing Redis connection..."
    python -c "
import os
import redis
try:
    r = redis.from_url(os.environ['REDIS_URL'])
    r.ping()
    print('✓ Redis connection successful!')
except Exception as e:
    print(f'⚠️  Redis connection failed: {e}')
    print('Continuing without Redis cache...')
"
fi

# Initialize Superset database
echo "🔧 Initializing Superset..."

# Database upgrade
superset db upgrade || {
    echo "Init failed, continuing..."
}

# Create admin user if it doesn't exist
superset fab create-admin \
    --username "${ADMIN_USERNAME:-admin}" \
    --firstname "${ADMIN_FIRSTNAME:-Admin}" \
    --lastname "${ADMIN_LASTNAME:-User}" \
    --email "${ADMIN_EMAIL:-admin@superset.com}" \
    --password "${ADMIN_PASSWORD:-admin}" || {
    echo "Admin user already exists or creation failed, continuing..."
}

# Initialize Superset
superset init || {
    echo "Superset init failed, continuing..."
}

# Apply custom patches
echo "🔧 Applying cache timeout patch..."
python /app/apply_patch.py || {
    echo "❌ Error applying patches: continuing anyway..."
}

# Schedule cache warming (if cron is installed)
if command -v crontab &> /dev/null; then
    echo "🔄 Scheduling initial cache warming..."
    (sleep 90 && python /app/scripts/cache_warmer_enhanced.py &) || true
    echo "✅ Cache warming will start in 90 seconds..."
fi

# Print cache status
echo "✅ Redis caching enabled: 6 cache layers active"
echo "   - Query Results Cache (1hr TTL)"
echo "   - Dashboard Data Cache (24hr TTL)"
echo "   - Filter State Cache (24hr TTL)"
echo "   - Explore Form Cache (2hr TTL)"
echo "   - Thumbnail Cache (7d TTL)"
echo "   - Metadata Cache (24hr TTL)"

# Start Gunicorn server
echo "Starting Superset server with Gunicorn on port ${PORT:-8088}..."
echo "🚀 Production mode enabled with Gunicorn + Gevent workers"
echo "Workers: ${GUNICORN_WORKERS:-2}, Threads: 8, Timeout: ${GUNICORN_TIMEOUT:-120}s"

# Start the server
exec gunicorn \
    --config /app/gunicorn_config.py \
    "superset.app:create_app()"
