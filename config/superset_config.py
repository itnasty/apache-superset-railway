import os

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

ENABLE_PROXY_FIX = True

SECRET_KEY = os.environ.get("SECRET_KEY")

# Database configuration - supports both DATABASE and DATABASE_URL
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE")

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
