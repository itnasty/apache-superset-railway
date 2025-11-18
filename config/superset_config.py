import os
from typing import Any, Dict, Optional
from datetime import timedelta
from functools import wraps
import sqlalchemy
from sqlalchemy.pool import NullPool

# Read database URL from environment
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

# If DATABASE_URL is not set, this will cause an error
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("DATABASE_URL environment variable is not set!")

# CRITICAL FIX: Comprehensive monkey-patch for SQLAlchemy's create_engine
# This fixes the "'int' object has no attribute 'total_seconds'" error
_original_create_engine = sqlalchemy.create_engine

@wraps(_original_create_engine)
def _patched_create_engine(*args, **kwargs):
    """
    Wrapper around SQLAlchemy's create_engine that properly handles
    all timeout and pool-related parameters.
    """
    # Handle pool_recycle conversion
    if 'pool_recycle' in kwargs:
        pool_recycle_value = kwargs['pool_recycle']
        if isinstance(pool_recycle_value, int) and pool_recycle_value > 0:
            # SQLAlchemy expects pool_recycle as int (seconds), not timedelta
            # Keep it as int
            print(f"🔧 pool_recycle set to {pool_recycle_value} seconds")
        elif pool_recycle_value == 0 or pool_recycle_value is None:
            kwargs.pop('pool_recycle', None)
            print("🔧 Removed pool_recycle (was 0 or None)")
    
    # Ensure pool_timeout is an integer
    if 'pool_timeout' in kwargs:
        pool_timeout_value = kwargs['pool_timeout']
        if not isinstance(pool_timeout_value, (int, float)):
            try:
                kwargs['pool_timeout'] = int(pool_timeout_value)
                print(f"🔧 Converted pool_timeout to int: {kwargs['pool_timeout']}")
            except (TypeError, ValueError):
                kwargs.pop('pool_timeout', None)
                print("🔧 Removed invalid pool_timeout")
    
    # Clean up connect_args if present
    if 'connect_args' in kwargs and isinstance(kwargs['connect_args'], dict):
        connect_args = kwargs['connect_args']
        # Ensure connect_timeout is an integer
        if 'connect_timeout' in connect_args:
            try:
                connect_args['connect_timeout'] = int(connect_args['connect_timeout'])
            except (TypeError, ValueError):
                connect_args.pop('connect_timeout', None)
    
    return _original_create_engine(*args, **kwargs)

# Replace SQLAlchemy's create_engine with our patched version
sqlalchemy.create_engine = _patched_create_engine
print("✅ SQLAlchemy create_engine patched successfully")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": REDIS_HOST,
}

DATA_CACHE_CONFIG = CACHE_CONFIG

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
# These are applied to Superset's own metadata database
SQLALCHEMY_POOL_SIZE = int(os.environ.get("SQLALCHEMY_POOL_SIZE", "10"))
SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get("SQLALCHEMY_MAX_OVERFLOW", "20"))
SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get("SQLALCHEMY_POOL_TIMEOUT", "30"))
SQLALCHEMY_POOL_PRE_PING = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Engine options for Superset's metadata database
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_size": SQLALCHEMY_POOL_SIZE,
    "max_overflow": SQLALCHEMY_MAX_OVERFLOW,
    "pool_timeout": SQLALCHEMY_POOL_TIMEOUT,
    "pool_recycle": 1800,  # Recycle connections after 30 minutes
}

# DB_CONNECTION_MUTATOR for user-added data source connections
def DB_CONNECTION_MUTATOR(url, params, username, security_manager, source):
    """
    Mutator function for database connections added through the UI.
    Ensures proper parameter types and connection settings.
    
    CRITICAL: NullPool doesn't accept pooling parameters and needs minimal config!
    """
    try:
        # Check if NullPool is being used
        poolclass = params.get('poolclass', None)
        is_null_pool = poolclass is NullPool or (
            isinstance(poolclass, type) and issubclass(poolclass, NullPool)
        )
        
        # Log the pool class for debugging
        db_name = getattr(url, 'database', 'unknown')
        print(f"🔍 DB_CONNECTION_MUTATOR for database: {db_name}")
        print(f"   Pool class: {poolclass}")
        
        # For NullPool, use minimal configuration
        if is_null_pool:
            print(f"⚠️  NullPool detected - using minimal configuration")
            
            # Remove pool_pre_ping for NullPool (doesn't make sense without a pool)
            if 'pool_pre_ping' in params:
                params.pop('pool_pre_ping')
                print(f"   Removed pool_pre_ping (not needed for NullPool)")
            
            # Remove any pool sizing parameters
            for param in ['pool_size', 'max_overflow', 'pool_timeout', 'pool_recycle']:
                if param in params:
                    print(f"   Removing {param} (not compatible with NullPool)")
                    params.pop(param)
            
            # For NullPool, keep connect_args minimal
            # Don't add connect_timeout - let pymysql/driver use defaults
            if 'connect_args' not in params:
                params['connect_args'] = {}
            
            print(f"   Using driver defaults for connection timeout")
            
        else:
            # For regular pooling (QueuePool, etc.), add pool parameters
            print(f"✅ Regular pooling detected - adding pool parameters")
            
            # Ensure pool_pre_ping is enabled for reliability
            if 'pool_pre_ping' not in params:
                params['pool_pre_ping'] = True
            
            # Set reasonable pool sizes for data source connections
            if 'pool_size' not in params:
                params['pool_size'] = 5
            if 'max_overflow' not in params:
                params['max_overflow'] = 10
            if 'pool_timeout' not in params:
                params['pool_timeout'] = 30
            if 'pool_recycle' not in params:
                params['pool_recycle'] = 1800
            
            # Ensure all pool parameters are correct types
            for param in ['pool_size', 'max_overflow', 'pool_timeout', 'pool_recycle']:
                if param in params:
                    try:
                        params[param] = int(params[param])
                    except (TypeError, ValueError):
                        print(f"⚠️  Invalid {param} value, removing")
                        params.pop(param, None)
            
            # Initialize connect_args if not present
            if 'connect_args' not in params:
                params['connect_args'] = {}
            
            # Set connection timeout for regular pools
            if 'connect_timeout' not in params['connect_args']:
                params['connect_args']['connect_timeout'] = TEST_DATABASE_CONNECTION_TIMEOUT
            
            # Ensure connect_timeout is an integer
            if 'connect_timeout' in params['connect_args']:
                try:
                    params['connect_args']['connect_timeout'] = int(params['connect_args']['connect_timeout'])
                except (TypeError, ValueError):
                    params['connect_args']['connect_timeout'] = TEST_DATABASE_CONNECTION_TIMEOUT
        
        print(f"✅ DB_CONNECTION_MUTATOR completed for database: {db_name}")
        
    except Exception as e:
        print(f"❌ Error in DB_CONNECTION_MUTATOR: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just log the error
    
    return url, params

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

# Mapbox API key (optional)
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")
