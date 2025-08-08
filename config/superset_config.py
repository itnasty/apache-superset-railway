import os

# Flask App Config
ROW_LIMIT = 50000
SUPERSET_WEBSERVER_TIMEOUT = 600
SECRET_KEY = os.environ.get("SECRET_KEY", "ThisIsNotSecureChangeIt123")

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False

# Database
DATABASE_URL = os.environ.get("DATABASE") or os.environ.get("DATABASE_URL", "sqlite:////app/data/superset.db")
SQLALCHEMY_DATABASE_URI = DATABASE_URL

# Redis Configuration for Caching
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    # Parse Redis URL for cache configuration
    from urllib.parse import urlparse
    redis_parsed = urlparse(REDIS_URL)
    
    # Results Backend using Redis
    RESULTS_BACKEND = {
        "cache_type": "RedisCache",
        "cache_redis_host": redis_parsed.hostname,
        "cache_redis_port": redis_parsed.port or 6379,
        "cache_redis_password": redis_parsed.password,
        "cache_redis_db": 0,
        "cache_key_prefix": "superset_results_",
    }
    
    # Data Cache Config 
    DATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_data_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 1,
    }
    
    # Filter State Cache
    FILTER_STATE_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_filter_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 2,
    }
    
    # Explore Form Data Cache
    EXPLORE_FORM_DATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_explore_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 3,
    }

# Fix for dashboards - DISABLE async queries
GLOBAL_ASYNC_QUERIES = False
SUPERSET_LOAD_CHART_ASYNC = False

# Sequential chart loading for dashboards
CONCURRENT_CHART_LOAD_LIMIT = 1

# CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "origins": ["*"]
}

# Session
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# For Railway
ENABLE_PROXY_FIX = True
PREFERRED_URL_SCHEME = "https"

# Extended timeouts
DATABASE_QUERY_TIMEOUT = 300
WEB_QUERY_TIMEOUT = 600
SQLLAB_TIMEOUT = 600
