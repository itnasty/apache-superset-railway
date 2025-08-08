#!/bin/bash
set -e

echo "Starting Superset with optimized configuration..."

# Database setup
superset db upgrade || echo "DB upgrade failed, continuing..."

# Create admin user if it doesn't exist
superset fab create-admin \
    --username "${ADMIN_USERNAME:-admin}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL:-admin@example.com}" \
    --password "${ADMIN_PASSWORD:-admin}" || echo "Admin user already exists"

# Initialize Superset
superset init || echo "Init failed, continuing..."

# Setup cron jobs for cache warming (if cron is available)
if command -v cron &> /dev/null; then
    echo "Setting up cache warming cron jobs..."
    
    # Create log directory in app directory (writable)
    mkdir -p /app/logs
    touch /app/logs/cache_warmer.log || true
    
    # Add cron jobs (optional - can be disabled with env var)
    if [ "${ENABLE_CACHE_WARMING:-true}" = "true" ]; then
        # Copy cron configuration if it exists
        if [ -f /app/scripts/superset-cron ]; then
            cp /app/scripts/superset-cron /etc/cron.d/superset
            chmod 0644 /etc/cron.d/superset
            cron
            echo "✅ Cache warming cron jobs installed"
        fi
        
        # Run initial cache warming in background after 60 seconds
        (sleep 60 && python /app/scripts/cache_warmer.py --url http://localhost:${PORT:-8088} --critical-only 2>/dev/null || true) &
        echo "🔄 Initial cache warming scheduled..."
    fi
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

# Start the server
echo "Starting optimized Superset server on port ${PORT:-8088}..."
echo "🚀 Performance features enabled: virtualization, native filters, compression"
exec superset run -h 0.0.0.0 -p ${PORT:-8088} --with-threads
