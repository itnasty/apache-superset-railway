#!/bin/bash
set -e

echo "🚀 Starting Superset initialization..."

# Check database configuration (Railway provides DATABASE variable)
DATABASE_URL=${DATABASE:-${DATABASE_URL:-"sqlite:////app/data/superset.db"}}
echo "🗄️  Using database: $(echo $DATABASE_URL | sed 's/:[^:]*@/@***@/g')"

# Wait a moment for any database connections to be ready
sleep 3

echo "📊 Upgrading database first..."
# Upgrade Superset database before creating users
superset db upgrade

echo "👤 Creating admin user..."
# Create Admin user using Railway-provided environment variables
superset fab create-admin \
    --username "${ADMIN_USERNAME}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL}" \
    --password "${ADMIN_PASSWORD}" || {
        echo "⚠️  Admin user creation failed or user already exists"
    }

echo "🔧 Initializing Superset roles and permissions..."
# Setup roles and permissions
superset init

echo "✅ Superset initialization complete!"

# Export Railway domain for CORS if available
if [ ! -z "$RAILWAY_PUBLIC_DOMAIN" ]; then
    echo "🌐 Railway domain detected: $RAILWAY_PUBLIC_DOMAIN"
    export SUPERSET_WEBSERVER_DOMAINS="$RAILWAY_PUBLIC_DOMAIN"
fi

echo "🌐 Starting web server on port ${PORT:-8088}..."

# Check if we should use gunicorn for better performance
if [ "$USE_GUNICORN" = "true" ]; then
    echo "🚀 Starting with Gunicorn for better performance..."
    exec gunicorn \
        --bind "0.0.0.0:${PORT:-8088}" \
        --workers ${GUNICORN_WORKERS:-2} \
        --worker-class ${GUNICORN_WORKER_CLASS:-gevent} \
        --timeout ${GUNICORN_TIMEOUT:-600} \
        --keepalive ${GUNICORN_KEEPALIVE:-2} \
        --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
        --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
        --access-logfile - \
        --error-logfile - \
        "superset.app:create_app()"
else
    # Start web server using Railway's PORT variable with development server
    exec superset run -h 0.0.0.0 -p ${PORT:-8088} --with-threads --reload --debugger
fi
