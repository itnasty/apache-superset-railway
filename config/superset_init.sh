#!/bin/bash
set -e

echo "🚀 Starting Superset initialization..."

# Check if we have a DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  No DATABASE_URL found, using SQLite default"
    export DATABASE_URL="sqlite:////app/data/superset.db"
fi

echo "🗄️  Database URL: $DATABASE_URL"

# Wait a moment for any database connections to be ready
sleep 3

echo "📊 Upgrading database first..."
# Upgrade Superset database before creating users
superset db upgrade

echo "👤 Creating admin user..."
# Create Admin user (this command is idempotent)
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
echo "🌐 Starting web server on port 8088..."

# Start web server
exec superset run -h 0.0.0.0 -p 8088
