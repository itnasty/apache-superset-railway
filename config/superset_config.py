import os
from typing import Any, Dict, Optional
from datetime import timedelta

# Read database URL from environment
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

# If DATABASE_URL is not set, this will cause an error
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("DATABASE_URL environment variable is not set!")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": REDIS_HOST,
}

# Celery configuration for async queries
class CeleryConfig:
    broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    result_backend = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    worker_prefetch_multiplier = 1
    task_acks_late = True

CELERY_CONFIG = CeleryConfig

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET")

# Timeout configurations
TEST_DATABASE_CONNECTION_TIMEOUT = int(os.environ.get("TEST_DATABASE_CONNECTION_TIMEOUT", "120"))
SQLLAB_TIMEOUT = int(os.environ.get("SQLLAB_TIMEOUT", "300"))
SUPERSET_WEBSERVER_TIMEOUT = int(os.environ.get("SUPERSET_WEBSERVER_TIMEOUT", "300"))

# SQLAlchemy connection pool settings for metadata database
SQLALCHEMY_POOL_SIZE = int(os.environ.get("SQLALCHEMY_POOL_SIZE", "10"))
SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get("SQLALCHEMY_MAX_OVERFLOW", "20"))
SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get("SQLALCHEMY_POOL_TIMEOUT", "30"))
SQLALCHEMY_POOL_PRE_PING = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CRITICAL FIX: Custom hook to modify database engine parameters
# This function is called by Superset when creating database engines
def DB_CONNECTION_MUTATOR(
    uri: str,
    params: Dict[str, Any],
    username: Optional[str],
    security_manager: Any,
    source: Any,
) -> None:
    """
    Mutator to fix the pool_recycle issue for ALL database connections.
    Superset's MySQL engine spec sets pool_recycle as an integer, but
    SQLAlchemy 2.x requires a timedelta object.
    """
    # Check if pool_recycle exists and is an integer
    if 'pool_recycle' in params:
        pool_recycle_value = params['pool_recycle']
        if isinstance(pool_recycle_value, int):
            # Convert integer to timedelta
            params['pool_recycle'] = timedelta(seconds=pool_recycle_value)
            print(f"✅ Converted pool_recycle from {pool_recycle_value} (int) to timedelta")
        elif pool_recycle_value is None or pool_recycle_value == 0:
            # Remove if None or 0
            params.pop('pool_recycle', None)
            print("✅ Removed pool_recycle (was None or 0)")
    
    # Ensure pool_pre_ping is enabled for connection health checks
    params['pool_pre_ping'] = True
    
    print(f"✅ DB_CONNECTION_MUTATOR applied for {uri[:50]}...")

# Engine options
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
}

# Allow connecting to private databases
PREVENT_UNSAFE_DB_CONNECTIONS = os.environ.get("PREVENT_UNSAFE_DB_CONNECTIONS", "false").lower() == "true"

# Web server configuration
SUPERSET_WEBSERVER_PORT = int(os.environ.get("PORT", "8088"))
SUPERSET_WEBSERVER_ADDRESS = "0.0.0.0"
SUPERSET_WEBSERVER_PROTOCOL = os.environ.get("SUPERSET_WEBSERVER_PROTOCOL", "http")

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Load examples
SUPERSET_LOAD_EXAMPLES = os.environ.get("SUPERSET_LOAD_EXAMPLES", "no").lower() in ["yes", "true", "1"]

# CSRF Protection
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Flask environment
FLASK_ENV = os.environ.get("FLASK_ENV", "production")

# Enable proxy fix for Railway
ENABLE_PROXY_FIX = True
