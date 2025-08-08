#!/bin/bash
set -e

echo "Starting Superset..."

# Database setup
superset db upgrade

# Create admin user if it doesn't exist
superset fab create-admin \
    --username "${ADMIN_USERNAME}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL}" \
    --password "${ADMIN_PASSWORD}" || echo "Admin user already exists"

# Initialize Superset
superset init

# Start the server
exec superset run -h 0.0.0.0 -p ${PORT:-8088} --with-threads --reload
