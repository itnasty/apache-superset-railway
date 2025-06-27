import os

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

ENABLE_PROXY_FIX = True

SECRET_KEY = os.environ.get("SECRET_KEY")

# Database configuration - Railway provides DATABASE_URL, fallback to our default
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to SQLite if no DATABASE_URL is provided
    DATABASE_URL = "sqlite:////app/data/superset.db"

SQLALCHEMY_DATABASE_URI = DATABASE_URL

# Ensure SQLite uses absolute paths and proper settings
if DATABASE_URL.startswith("sqlite://"):
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"check_same_thread": False}
    }

# Redis configuration for caching (optional)
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL
    }

# Security settings
TALISMAN_ENABLED = True
WTF_CSRF_ENABLED = True

# Disable some features that might cause issues in containerized environments
ENABLE_CHUNK_ENCODING = False
