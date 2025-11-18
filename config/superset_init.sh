#!/bin/bash
set -e

echo "Starting Superset initialization..."

# Upgrade database first
echo "Upgrading Superset metastore..."
superset db upgrade

# Create or update admin user
echo "Setting up admin user..."
if superset fab create-admin \
    --username "$ADMIN_USERNAME" \
    --firstname Superset \
    --lastname Admin \
    --email "$ADMIN_EMAIL" \
    --password "$ADMIN_PASSWORD"; then
    echo "✅ Admin user created successfully"
else
    echo "⚠️  Admin user already exists, resetting password..."
    superset fab reset-password --username "$ADMIN_USERNAME" --password "$ADMIN_PASSWORD"
    echo "✅ Admin password reset successfully"
fi

# Setup roles and permissions
echo "Initializing roles and permissions..."
superset init

# Start server
echo "Starting Superset server..."
/bin/sh -c /usr/bin/run-server.sh
