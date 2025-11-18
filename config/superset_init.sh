#!/bin/bash
set -e

echo "Starting Superset initialization..."

# Extract database connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

echo "🔧 Fixing Alembic migration state..."

# Use Python to fix the alembic version table
python3 << PYTHON_EOF
import os
from sqlalchemy import create_engine, text

database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)

with engine.connect() as conn:
    # Check if alembic_version table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'alembic_version'
        );
    """))
    
    table_exists = result.scalar()
    
    if table_exists:
        print("📋 Checking current alembic version...")
        result = conn.execute(text("SELECT * FROM alembic_version;"))
        versions = result.fetchall()
        
        if versions:
            print(f"Found versions: {versions}")
            print("🗑️  Deleting problematic alembic version...")
            conn.execute(text("DELETE FROM alembic_version;"))
            conn.commit()
            print("✅ Alembic version table cleared")
        else:
            print("ℹ️  Alembic version table is already empty")
    else:
        print("ℹ️  Alembic version table doesn't exist yet")

engine.dispose()
print("✅ Migration state fixed")
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
