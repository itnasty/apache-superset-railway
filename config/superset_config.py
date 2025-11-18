import os
from typing import Any, Dict, Optional

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

# CRITICAL FIX: Hook into Superset's database engine creation
# This function is called whenever Superset creates a database engine (for external databases)
def DB_CONNECTION_MUTATOR(
    uri: str,
    params: Dict[str, Any],
    username: Optional[str],
    security_manager: Any,
    source: Any,
) -> None:
    """
    Mutator function to modify database connection parameters.
    This prevents the pool_recycle error by removing it from params.
    """
    # Remove pool_recycle if it exists to prevent the total_seconds error
    params.pop('pool_recycle', None)
    
    # Set safe connection pool parameters
    params['pool_pre_ping'] = True
    params['pool_size'] = 5
    params['max_overflow'] = 10
    params['pool_timeout'] = 30

# Engine options - DO NOT include pool_recycle
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
