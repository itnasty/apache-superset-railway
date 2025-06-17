#!/bin/bash
echo "✅ Superset Init Script Started..."

# Create Admin user (won’t crash if user already exists)
superset fab create-admin \
    --username "${ADMIN_USERNAME}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL}" \
    --password "${ADMIN_PASSWORD}" || true

# Upgrade Superset database
superset db upgrade

# Setup roles and permissions
superset init

# Start web server
superset run -h 0.0.0.0 -p 8088
