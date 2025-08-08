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
else:
    # For other databases, use environment variables if provided
    engine_options = os.environ.get("SQLALCHEMY_ENGINE_OPTIONS")
    if engine_options:
        try:
            SQLALCHEMY_ENGINE_OPTIONS = json.loads(engine_options)
        except json.JSONDecodeError:
            # If JSON parsing fails, use default
            pass

# Redis configuration for caching
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    # Main cache configuration
    cache_config = os.environ.get("CACHE_CONFIG")
    if cache_config:
        try:
            CACHE_CONFIG = json.loads(cache_config)
        except json.JSONDecodeError:
            CACHE_CONFIG = {
                'CACHE_TYPE': 'RedisCache',
                'CACHE_REDIS_URL': REDIS_URL,
                'CACHE_DEFAULT_TIMEOUT': 300,
                'CACHE_KEY_PREFIX': 'superset_'
            }
    else:
        CACHE_CONFIG = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': REDIS_URL,
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'superset_'
        }
    
    # Data cache configuration
    DATA_CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL,
        'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
        'CACHE_KEY_PREFIX': 'superset_data_'
    }
    
    # Filter state cache configuration
    FILTER_STATE_CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL,
        'CACHE_DEFAULT_TIMEOUT': 86400,
        'CACHE_KEY_PREFIX': 'superset_filter_'
    }
    
    # Explore form data cache configuration
    EXPLORE_FORM_DATA_CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL,
        'CACHE_DEFAULT_TIMEOUT': 86400,
        'CACHE_KEY_PREFIX': 'superset_explore_'
    }
else:
    # Use simple cache if no Redis
    CACHE_CONFIG = {
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
    }
    DATA_CACHE_CONFIG = {
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 86400,
    }
    FILTER_STATE_CACHE_CONFIG = {
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 86400,
    }
    EXPLORE_FORM_DATA_CACHE_CONFIG = {
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 86400,
    }

# Mapbox configuration
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")

# Feature flags - CRITICAL DASHBOARD SETTINGS
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ENABLE_JAVASCRIPT_CONTROLS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDABLE_CHARTS": True,
    "SCHEDULED_QUERIES": True,
    "ESTIMATE_QUERY_COST": True,
    "GLOBAL_ASYNC_QUERIES": False,  # DISABLED for Railway
    "DASHBOARD_VIRTUALIZATION": False,
    "DISABLE_DATASET_SOURCE_EDIT": False,
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DISABLE_LEGACY_DATASOURCE_EDITOR": True,
    "VERSIONED_EXPORT": True,
    "DASHBOARD_CACHE": True,
    "REMOVE_SLICE_LEVEL_LABEL_COLORS": False,
    "ENABLE_REACT_CRUD_VIEWS": True,
    "DISABLE_DATASET_SOURCE_EDIT": False,
}

# Override with environment variable if provided
feature_flags = os.environ.get("SUPERSET_FEATURE_FLAGS")
if feature_flags:
    try:
        FEATURE_FLAGS.update(json.loads(feature_flags))
    except json.JSONDecodeError:
        pass

# Security settings
ENABLE_PROXY_FIX = os.environ.get("ENABLE_PROXY_FIX", "True").lower() == "true"
TALISMAN_ENABLED = os.environ.get("TALISMAN_ENABLED", "False").lower() == "true"
WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "False").lower() == "true"
WTF_CSRF_TIME_LIMIT = None  # Disable CSRF time limit

# CSRF settings - VERY PERMISSIVE FOR DEBUGGING
WTF_CSRF_EXEMPT_LIST = [
    "superset.views.api",
    "superset.views.core.api",
    "superset.charts.api",
    "superset.charts.data.api",
    "superset.dashboards.api",
    "superset.explore.api",
    "superset.sqllab.api",
    "superset.datasource.api",
    "superset.queries.api",
    "superset.datasets.api",
    "superset.databases.api",
    "superset.views.core.data",
    "superset.views.core.get_data",
    "superset.views.core.datasource",
    "superset.connectors.sqla.views.TableModelView",
    "superset.superset.views.core.Superset",
    "superset.views.dashboard.api",
    "superset.views.chart.api",
]

# CORS settings - MAXIMUM PERMISSIVENESS
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "origins": ["*"],
    "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
    "send_wildcard": True,
    "always_send": True,
}

# HTTP Headers - Disable security headers that might interfere
HTTP_HEADERS = {}
OVERRIDE_HTTP_HEADERS = {}

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
SUPERSET_META_DB_LIMIT = int(os.environ.get("SUPERSET_META_DB_LIMIT", 1000))

# MAXIMUM TIMEOUTS
WEB_QUERY_TIMEOUT = int(os.environ.get("WEB_QUERY_TIMEOUT", 900))  # 15 minutes
DATABASE_QUERY_TIMEOUT = int(os.environ.get("DATABASE_QUERY_TIMEOUT", 300))  # 5 minutes
SUPERSET_WEBSERVER_TIMEOUT = int(os.environ.get("SUPERSET_WEBSERVER_TIMEOUT", 900))  # 15 minutes
SQLLAB_TIMEOUT = int(os.environ.get("SQLLAB_TIMEOUT", 900))  # 15 minutes
SQLLAB_ASYNC_TIME_LIMIT_SEC = int(os.environ.get("SQLLAB_ASYNC_TIME_LIMIT_SEC", 43200))  # 12 hours

# DISABLE ASYNC QUERIES FOR DASHBOARDS
GLOBAL_ASYNC_QUERIES = False
SUPERSET_LOAD_CHART_ASYNC = False

# Dashboard specific settings
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

# Webserver domains
superset_webserver_domains = os.environ.get("SUPERSET_WEBSERVER_DOMAINS")
if superset_webserver_domains:
    SUPERSET_WEBSERVER_DOMAINS = superset_webserver_domains.split(",")

# Session configuration
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False  # Set to False for debugging
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# Preferred URL scheme
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

# Public role configuration
AUTH_ROLE_PUBLIC = os.environ.get("AUTH_ROLE_PUBLIC", "Gamma")
PUBLIC_ROLE_LIKE = os.environ.get("PUBLIC_ROLE_LIKE", "Gamma")

# Guest role configuration
GUEST_ROLE_NAME = os.environ.get("GUEST_ROLE_NAME", "Gamma")

# Disable some features that might cause issues
ENABLE_CHUNK_ENCODING = False

# SEQUENTIAL CHART LOADING FOR DASHBOARDS
CONCURRENT_CHART_LOAD_LIMIT = 1  # Load one chart at a time

# Dashboard cache configuration
DASHBOARD_CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# Chart cache configuration
CHART_CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
}

# Additional module DS map
additional_module_ds_map = os.environ.get("ADDITIONAL_MODULE_DS_MAP")
if additional_module_ds_map:
    try:
        ADDITIONAL_MODULE_DS_MAP = json.loads(additional_module_ds_map)
    except json.JSONDecodeError:
        pass

# Dashboard virtualization - DISABLED
DASHBOARD_VIRTUALIZATION = False

# Preferred databases
preferred_databases = os.environ.get("PREFERRED_DATABASES")
if preferred_databases:
    try:
        PREFERRED_DATABASES = json.loads(preferred_databases)
    except json.JSONDecodeError:
        pass

# Other settings from environment
if os.environ.get("SUPERSET_UPDATE_PERMS"):
    SUPERSET_UPDATE_PERMS = int(os.environ.get("SUPERSET_UPDATE_PERMS"))

if os.environ.get("SUPERSET_LOAD_EXAMPLES"):
    SUPERSET_LOAD_EXAMPLES = int(os.environ.get("SUPERSET_LOAD_EXAMPLES"))

# Set content security policy warning off
CONTENT_SECURITY_POLICY_WARNING = False

# Ensure all API endpoints work properly
API_ENABLE_CORS = True

# Additional settings for Railway deployment
COMPRESS_ENABLED = True
COMPRESS_REGISTER = True

# Gunicorn worker configuration
GUNICORN_BIND = f"0.0.0.0:{os.environ.get('PORT', 8088)}"
GUNICORN_WORKERS = int(os.environ.get("GUNICORN_WORKERS", 2))
GUNICORN_WORKER_CLASS = os.environ.get("GUNICORN_WORKER_CLASS", "sync")  # Changed from gevent to sync
GUNICORN_TIMEOUT = int(os.environ.get("GUNICORN_TIMEOUT", 900))
GUNICORN_KEEPALIVE = int(os.environ.get("GUNICORN_KEEPALIVE", 2))
GUNICORN_MAX_REQUESTS = int(os.environ.get("GUNICORN_MAX_REQUESTS", 1000))
GUNICORN_MAX_REQUESTS_JITTER = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 50))

# Prevent URL encoding issues
SEND_FILE_MAX_AGE_DEFAULT = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", 86400))

# Default feature flags
DEFAULT_FEATURE_FLAGS = FEATURE_FLAGS.copy()

# Application configuration
APP_NAME = "Superset"
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

# Flask app config
SEND_FILE_MAX_AGE_DEFAULT = 86400
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max request size

# Dashboard loading optimization
DASHBOARD_TEMPLATE_ID_KEY = "_dashboard_template_id"
STORE_CACHE_KEYS_IN_METADATA_DB = False

# Logging configuration
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Enable debug mode for troubleshooting
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
FLASK_DEBUG = DEBUG

# API rate limiting - disabled for debugging
RATELIMIT_ENABLED = False

# Results backend - use database if no Redis
if REDIS_URL:
    RESULTS_BACKEND = {
        "class": "cachelib.redis.RedisCache",
        "cache_redis_url": REDIS_URL,
        "key_prefix": "superset_results",
    }
else:
    RESULTS_BACKEND = None

# SQL Lab configuration
SQL_QUERY_MUTATOR = None
SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_DEFAULT_DBID = None
SQLLAB_VALIDATION_TIMEOUT = 10
SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT = 10

# Chart rendering
SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

print("=" * 80)
print("SUPERSET CONFIGURATION LOADED")
print(f"ASYNC QUERIES: {GLOBAL_ASYNC_QUERIES}")
print(f"ASYNC CHART LOAD: {SUPERSET_LOAD_CHART_ASYNC}")
print(f"CONCURRENT CHART LIMIT: {CONCURRENT_CHART_LOAD_LIMIT}")
print(f"WEB TIMEOUT: {WEB_QUERY_TIMEOUT}")
print(f"CSRF ENABLED: {WTF_CSRF_ENABLED}")
print(f"CORS ENABLED: {ENABLE_CORS}")
print(f"WORKER CLASS: {GUNICORN_WORKER_CLASS}")
print("=" * 80)
