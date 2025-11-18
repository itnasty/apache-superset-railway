#!/bin/bash
set -e

echo "Starting Superset initialization..."

echo "🔧 Resetting database schema..."

# Use Python to completely reset the database
python3 << PYTHON_EOF
import os
from sqlalchemy import create_engine, text

database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url, isolation_level="AUTOCOMMIT")

print("⚠️  WARNING: Dropping all existing tables and recreating schema...")
print("This will delete all existing Superset data!")

# Use AUTOCOMMIT isolation level for DDL statements
with engine.connect() as conn:
    # Drop the public schema and recreate it
    conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    
print("✅ Database schema reset complete")
engine.dispose()
PYTHON_EOF

echo "Upgrading Superset metastore..."
superset db upgrade

echo "Initializing Superset..."
superset init

echo "Setting up admin user..."
superset fab create-admin \
    --username "${ADMIN_USERNAME}" \
    --firstname Superset \
    --lastname Admin \
    --email "${ADMIN_EMAIL}" \
    --password "${ADMIN_PASSWORD}" || true

echo "✅ Superset initialization complete!"

# Start Superset
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8088}" \
    --workers 4 \
    --worker-class gevent \
    --threads 4 \
    --timeout 300 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "superset.app:create_app()"
