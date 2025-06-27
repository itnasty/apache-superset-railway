#!/bin/bash
set -e

echo "🚀 Starting Superset initialization..."

# Wait a moment for any database connections to be ready
sleep 2

echo "📊 Creating admin user..."
# Create Admin user (won't crash if user already exists)
superset fab create-admin \
    --username "${ADMIN_USERNAME}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL}" \
    --password "${ADMIN_PASSWORD}" || echo "⚠️  Admin user might already exist"

echo "🔄 Upgrading database..."
# Upgrade Superset database
superset db upgrade

echo "🔧 Initializing Superset..."
# Setup roles and permissions
superset init

echo "✅ Superset initialization complete!"
echo "🌐 Starting web server on port 8088..."

# Start web server
superset run -h 0.0.0.0 -p 8088
