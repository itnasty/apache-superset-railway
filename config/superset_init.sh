#!/bin/bash
set -e

echo "Starting Superset..."

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

# Start the server
echo "Starting server on port ${PORT:-8088}..."
exec superset run -h 0.0.0.0 -p ${PORT:-8088} --with-threads
