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
    data_cache_config = os.environ.get("DATA_CACHE_CONFIG")
    if data_cache_config:
        try:
            DATA_CACHE_CONFIG = json.loads(data_cache_config)
        except json.JSONDecodeError:
            pass
    
    # Filter state cache configuration
    filter_state_cache_config = os.environ.get("FILTER_STATE_CACHE_CONFIG")
    if filter_state_cache_config:
        try:
            FILTER_STATE_CACHE_CONFIG = json.loads(filter_state_cache_config)
        except json.JSONDecodeError:
            pass
    
    # Explore form data cache configuration
    explore_form_data_cache_config = os.environ.get("EXPLORE_FORM_DATA_CACHE_CONFIG")
    if explore_form_data_cache_config:
        try:
            EXPLORE_FORM_DATA_CACHE_CONFIG = json.loads(explore_form_data_cache_config)
        except json.JSONDecodeError:
            pass
    
    # Results backend configuration
    results_backend = os.environ.get("RESULTS_BACKEND")
    if results_backend:
        try:
            RESULTS_BACKEND = json.loads(results_backend)
        except json.JSONDecodeError:
            pass
    
    # Thumbnail cache configuration
    thumbnail_cache_config = os.environ.get("THUMBNAIL_CACHE_CONFIG")
    if thumbnail_cache_config:
        try:
            THUMBNAIL_CACHE_CONFIG = json.loads(thumbnail_cache_config)
        except json.JSONDecodeError:
            pass
    
    # Celery configuration
    celery_config = os.environ.get("CELERY_CONFIG")
    if celery_config:
        try:
            CELERY_CONFIG = json.loads(celery_config)
        except json.JSONDecodeError:
            pass
    
    # Rate limit storage
    ratelimit_storage_uri = os.environ.get("RATELIMIT_STORAGE_URI")
    if ratelimit_storage_uri:
        RATELIMIT_STORAGE_URI = ratelimit_storage_uri

# Mapbox configuration
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")

# Feature flags - handle both Python True/False and JSON true/false
feature_flags = os.environ.get("SUPERSET_FEATURE_FLAGS")
if feature_flags:
    try:
        # First try to parse as JSON
        FEATURE_FLAGS = json.loads(feature_flags)
    except json.JSONDecodeError:
        # If that fails, try replacing Python booleans with JSON booleans
        try:
            feature_flags_fixed = feature_flags.replace("True", "true").replace("False", "false")
            FEATURE_FLAGS = json.loads(feature_flags_fixed)
        except json.JSONDecodeError:
            # If still fails, use default
            FEATURE_FLAGS = {
                "ENABLE_TEMPLATE_PROCESSING": True,
                "ENABLE_JAVASCRIPT_CONTROLS": True,
                "DASHBOARD_CROSS_FILTERS": True,
                "DASHBOARD_RBAC": True,
                "EMBEDDABLE_CHARTS": True,
                "SCHEDULED_QUERIES": True,
                "ESTIMATE_QUERY_COST": True,
                "GLOBAL_ASYNC_QUERIES": True,
                "DASHBOARD_VIRTUALIZATION": False,
                "DISABLE_DATASET_SOURCE_EDIT": False
            }
else:
    FEATURE_FLAGS = {
        "ENABLE_TEMPLATE_PROCESSING": True,
        "ENABLE_JAVASCRIPT_CONTROLS": True,
        "DASHBOARD_CROSS_FILTERS": True,
        "DASHBOARD_RBAC": True,
        "EMBEDDABLE_CHARTS": True,
        "SCHEDULED_QUERIES": True,
        "ESTIMATE_QUERY_COST": True,
        "GLOBAL_ASYNC_QUERIES": True,
        "DASHBOARD_VIRTUALIZATION": False,
        "DISABLE_DATASET_SOURCE_EDIT": False
    }

# Security settings
ENABLE_PROXY_FIX = os.environ.get("ENABLE_PROXY_FIX", "True").lower() == "true"
TALISMAN_ENABLED = os.environ.get("TALISMAN_ENABLED", "False").lower() == "true"
WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "False").lower() == "true"

# CSRF settings
csrf_exempt_list = os.environ.get("WTF_CSRF_EXEMPT_LIST")
if csrf_exempt_list:
    try:
        WTF_CSRF_EXEMPT_LIST = json.loads(csrf_exempt_list)
    except json.JSONDecodeError:
        WTF_CSRF_EXEMPT_LIST = ["superset.views.api", "superset.views.core.api", "superset.charts.api.ChartRestApi.post"]
else:
    WTF_CSRF_EXEMPT_LIST = ["superset.views.api", "superset.views.core.api", "superset.charts.api.ChartRestApi.post"]

# Add more CSRF exemptions for chart data endpoints
WTF_CSRF_EXEMPT_LIST.extend([
    "superset.charts.data.api.ChartDataRestApi.data",
    "superset.charts.data.api.ChartDataRestApi.get_data",
    "superset.charts.data.api.ChartDataRestApi.data_from_cache",
    "superset.dashboards.api",
    "superset.explore.api"
])

# CORS settings - CRITICAL FOR RAILWAY
ENABLE_CORS = os.environ.get("ENABLE_CORS", "True").lower() == "true"
cors_options = os.environ.get("CORS_OPTIONS")
if cors_options:
    try:
        CORS_OPTIONS = json.loads(cors_options)
    except json.JSONDecodeError:
        CORS_OPTIONS = {
            "supports_credentials": True,
            "allow_headers": ["*"],
            "expose_headers": ["X-CSRFToken"],
            "origins": ["*"],
            "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]
        }
else:
    CORS_OPTIONS = {
        "supports_credentials": True,
        "allow_headers": ["*"],
        "expose_headers": ["X-CSRFToken"],
        "origins": ["*"],
        "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]
    }

# HTTP Headers
http_headers = os.environ.get("HTTP_HEADERS")
if http_headers:
    try:
        HTTP_HEADERS = json.loads(http_headers)
    except json.JSONDecodeError:
        pass
else:
    HTTP_HEADERS = {}

# Proxy configuration for Railway
proxy_fix_config = os.environ.get("PROXY_FIX_CONFIG")
if proxy_fix_config:
    try:
        PROXY_FIX_CONFIG = json.loads(proxy_fix_config)
    except json.JSONDecodeError:
        PROXY_FIX_CONFIG = {
            "x_for": 1,
            "x_proto": 1,
            "x_host": 1,
            "x_port": 1,
            "x_prefix": 1
        }
else:
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

# INCREASED TIMEOUTS FOR RAILWAY
WEB_QUERY_TIMEOUT = int(os.environ.get("WEB_QUERY_TIMEOUT", 600))  # Increased from 300
DATABASE_QUERY_TIMEOUT = int(os.environ.get("DATABASE_QUERY_TIMEOUT", 120))  # Increased from 60
SUPERSET_WEBSERVER_TIMEOUT = int(os.environ.get("SUPERSET_WEBSERVER_TIMEOUT", 600))  # Increased from 300
SQLLAB_TIMEOUT = int(os.environ.get("SQLLAB_TIMEOUT", 600))  # Added
SQLLAB_ASYNC_TIME_LIMIT_SEC = int(os.environ.get("SQLLAB_ASYNC_TIME_LIMIT_SEC", 43200))  # 12 hours

# Async queries configuration - IMPROVED FOR DASHBOARDS
GLOBAL_ASYNC_QUERIES = os.environ.get("GLOBAL_ASYNC_QUERIES", "True").lower() == "true"
SUPERSET_LOAD_CHART_ASYNC = os.environ.get("SUPERSET_LOAD_CHART_ASYNC", "True").lower() == "true"

# Global async queries transport - CRITICAL FOR RAILWAY
GLOBAL_ASYNC_QUERIES_TRANSPORT = os.environ.get("GLOBAL_ASYNC_QUERIES_TRANSPORT", "polling")
GLOBAL_ASYNC_QUERIES_POLLING_DELAY = int(os.environ.get("GLOBAL_ASYNC_QUERIES_POLLING_DELAY", 500))

# Webserver domains
superset_webserver_domains = os.environ.get("SUPERSET_WEBSERVER_DOMAINS")
if superset_webserver_domains:
    SUPERSET_WEBSERVER_DOMAINS = superset_webserver_domains.split(",")

# Session configuration - FIXED FOR RAILWAY
SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")  # Changed from None
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "True").lower() == "true"  # Changed to True
SESSION_COOKIE_HTTPONLY = os.environ.get("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"  # Changed to True

# Preferred URL scheme
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

# Public role configuration
AUTH_ROLE_PUBLIC = os.environ.get("AUTH_ROLE_PUBLIC", "Gamma")
PUBLIC_ROLE_LIKE = os.environ.get("PUBLIC_ROLE_LIKE", "Gamma")

# Guest role configuration
GUEST_ROLE_NAME = os.environ.get("GUEST_ROLE_NAME", "Gamma")

# Disable some features that might cause issues in containerized environments
ENABLE_CHUNK_ENCODING = False

# INCREASED CHART LOAD LIMIT FOR DASHBOARDS
CONCURRENT_CHART_LOAD_LIMIT = int(os.environ.get("CONCURRENT_CHART_LOAD_LIMIT", 8))  # Increased from 4

# Additional module DS map
additional_module_ds_map = os.environ.get("ADDITIONAL_MODULE_DS_MAP")
if additional_module_ds_map:
    try:
        ADDITIONAL_MODULE_DS_MAP = json.loads(additional_module_ds_map)
    except json.JSONDecodeError:
        pass

# Dashboard virtualization - Keep disabled for now
DASHBOARD_VIRTUALIZATION = os.environ.get("DASHBOARD_VIRTUALIZATION", "False").lower() == "true"

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

# Set content security policy warning off since we're handling it differently
CONTENT_SECURITY_POLICY_WARNING = False

# Ensure all API endpoints work properly
API_ENABLE_CORS = True

# Additional settings for Railway deployment
COMPRESS_ENABLED = True
COMPRESS_REGISTER = True

# Gunicorn worker configuration (if using gunicorn)
GUNICORN_BIND = f"0.0.0.0:{os.environ.get('PORT', 8088)}"
GUNICORN_WORKERS = int(os.environ.get("GUNICORN_WORKERS", 2))
GUNICORN_WORKER_CLASS = os.environ.get("GUNICORN_WORKER_CLASS", "gevent")
GUNICORN_TIMEOUT = int(os.environ.get("GUNICORN_TIMEOUT", 600))
GUNICORN_KEEPALIVE = int(os.environ.get("GUNICORN_KEEPALIVE", 2))
GUNICORN_MAX_REQUESTS = int(os.environ.get("GUNICORN_MAX_REQUESTS", 1000))
GUNICORN_MAX_REQUESTS_JITTER = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 50))

# Prevent URL encoding issues
SEND_FILE_MAX_AGE_DEFAULT = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", 86400))

# Chart cache configuration
CHART_CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
}

# Dashboard filter configuration
DASHBOARD_NATIVE_FILTERS_SET = True
DEFAULT_FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
}
