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
echo "🌐 Starting web server on port ${PORT:-8088}..."

# Start web server using Railway's PORT variable
exec superset run -h 0.0.0.0 -p ${PORT:-8088}
