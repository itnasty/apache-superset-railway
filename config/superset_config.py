import os
import json

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "CoFEz4QHYKlnX4F7eoknGg0vxb6dA6DV")

# Database configuration - Railway provides DATABASE variable
DATABASE_URL = os.environ.get("DATABASE") or os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to SQLite if no database is provided
    DATABASE_URL = "sqlite:////app/data/superset.db"

SQLALCHEMY_DATABASE_URI = DATABASE_URL

# SQLAlchemy configuration
SQLALCHEMY_POOL_SIZE = int(os.environ.get("SQLALCHEMY_POOL_SIZE", 10))
SQLALCHEMY_POOL_RECYCLE = int(os.environ.get("SQLALCHEMY_POOL_RECYCLE", 300))
SQLALCHEMY_POOL_PRE_PING = os.environ.get("SQLALCHEMY_POOL_PRE_PING", "True").lower() == "true"
SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get("SQLALCHEMY_MAX_OVERFLOW", 2))

# Ensure SQLite uses absolute paths and proper settings
if DATABASE_URL.startswith("sqlite://"):
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"check_same_thread": False}
    }

# Redis configuration for caching
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL,
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'superset_'
    }
else:
    CACHE_CONFIG = {
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
    }

# Mapbox configuration
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ENABLE_JAVASCRIPT_CONTROLS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDABLE_CHARTS": True,
    "SCHEDULED_QUERIES": True,
    "ESTIMATE_QUERY_COST": True,
    "GLOBAL_ASYNC_QUERIES": os.environ.get("GLOBAL_ASYNC_QUERIES", "False").lower() == "true",
    "DASHBOARD_VIRTUALIZATION": False,
    "DISABLE_DATASET_SOURCE_EDIT": False,
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
}

# Security settings
ENABLE_PROXY_FIX = os.environ.get("ENABLE_PROXY_FIX", "True").lower() == "true"
TALISMAN_ENABLED = os.environ.get("TALISMAN_ENABLED", "False").lower() == "true"
WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "False").lower() == "true"
WTF_CSRF_TIME_LIMIT = None

# CSRF exemptions
WTF_CSRF_EXEMPT_LIST = [
    "superset.views.api",
    "superset.views.core.api",
    "superset.charts.api",
    "superset.charts.data.api",
    "superset.dashboards.api",
    "superset.explore.api",
    "superset.views.core.data",
]

# CORS settings
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "origins": ["*"],
    "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
}

# HTTP Headers
HTTP_HEADERS = {}

# Proxy configuration for Railway
ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {
    "x_for": 1,
    "x_proto": 1,
    "x_host": 1,
    "x_port": 1,
    "x_prefix": 1
}

# Query and row limits
ROW_LIMIT = int(os.environ.get("ROW_LIMIT", 50000))
VIZ_ROW_LIMIT = int(os.environ.get("VIZ_ROW_LIMIT", 10000))
SAMPLES_ROW_LIMIT = int(os.environ.get("SAMPLES_ROW_LIMIT", 1000))
FILTER_SELECT_ROW_LIMIT = int(os.environ.get("FILTER_SELECT_ROW_LIMIT", 10000))
SQL_MAX_ROW = int(os.environ.get("SQL_MAX_ROW", 100000))
DEFAULT_SQLLAB_LIMIT = int(os.environ.get("DEFAULT_SQLLAB_LIMIT", 1000))

# Timeouts
WEB_QUERY_TIMEOUT = int(os.environ.get("WEB_QUERY_TIMEOUT", 600))
DATABASE_QUERY_TIMEOUT = int(os.environ.get("DATABASE_QUERY_TIMEOUT", 300))
SUPERSET_WEBSERVER_TIMEOUT = int(os.environ.get("SUPERSET_WEBSERVER_TIMEOUT", 600))
SQLLAB_TIMEOUT = int(os.environ.get("SQLLAB_TIMEOUT", 600))
SQLLAB_ASYNC_TIME_LIMIT_SEC = int(os.environ.get("SQLLAB_ASYNC_TIME_LIMIT_SEC", 43200))

# Async queries configuration
GLOBAL_ASYNC_QUERIES = os.environ.get("GLOBAL_ASYNC_QUERIES", "False").lower() == "true"
SUPERSET_LOAD_CHART_ASYNC = os.environ.get("SUPERSET_LOAD_CHART_ASYNC", "False").lower() == "true"

# Global async queries transport
GLOBAL_ASYNC_QUERIES_TRANSPORT = os.environ.get("GLOBAL_ASYNC_QUERIES_TRANSPORT", "polling")
GLOBAL_ASYNC_QUERIES_POLLING_DELAY = int(os.environ.get("GLOBAL_ASYNC_QUERIES_POLLING_DELAY", 500))

# Session configuration
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 86400

# Preferred URL scheme
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

# Public role configuration
AUTH_ROLE_PUBLIC = os.environ.get("AUTH_ROLE_PUBLIC", "Gamma")
PUBLIC_ROLE_LIKE = os.environ.get("PUBLIC_ROLE_LIKE", "Gamma")

# Guest role configuration
GUEST_ROLE_NAME = os.environ.get("GUEST_ROLE_NAME", "Gamma")

# Disable some features that might cause issues
ENABLE_CHUNK_ENCODING = False

# Chart loading configuration
CONCURRENT_CHART_LOAD_LIMIT = int(os.environ.get("CONCURRENT_CHART_LOAD_LIMIT", 1))

# Set content security policy warning off
CONTENT_SECURITY_POLICY_WARNING = False

# Ensure all API endpoints work properly
API_ENABLE_CORS = True

# Additional settings for Railway deployment
COMPRESS_ENABLED = True
COMPRESS_REGISTER = True

# Prevent URL encoding issues
SEND_FILE_MAX_AGE_DEFAULT = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", 86400))

# Application configuration
APP_NAME = "Superset"
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

# Logging configuration
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Enable debug mode for troubleshooting
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
FLASK_DEBUG = DEBUG

# API rate limiting
RATELIMIT_ENABLED = False

# SQL Lab configuration
SQL_QUERY_MUTATOR = None
SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_DEFAULT_DBID = None
SQLLAB_VALIDATION_TIMEOUT = 10
SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT = 10

# Chart rendering
SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Dashboard cache configuration
DASHBOARD_CACHE_TIMEOUT = 60
DASHBOARD_AUTO_REFRESH_MODE = "fetch"
DASHBOARD_AUTO_REFRESH_INTERVALS = [
    [0, "Don't refresh"],
    [10, "10 seconds"],
    [30, "30 seconds"],
    [60, "1 minute"],
    [300, "5 minutes"],
    [1800, "30 minutes"],
    [3600, "1 hour"],
]

# Results backend
if REDIS_URL:
    RESULTS_BACKEND = {
        "class": "cachelib.redis.RedisCache",
        "cache_redis_url": REDIS_URL,
        "key_prefix": "superset_results",
    }
else:
    RESULTS_BACKEND = None

# Print configuration for debugging
print("=" * 60)
print("SUPERSET CONFIGURATION")
print(f"ASYNC QUERIES: {GLOBAL_ASYNC_QUERIES}")
print(f"ASYNC CHART LOAD: {SUPERSET_LOAD_CHART_ASYNC}")
print(f"CONCURRENT CHART LIMIT: {CONCURRENT_CHART_LOAD_LIMIT}")
print(f"WEB TIMEOUT: {WEB_QUERY_TIMEOUT}")
print(f"CSRF ENABLED: {WTF_CSRF_ENABLED}")
print(f"CORS ENABLED: {ENABLE_CORS}")
print("=" * 60)
