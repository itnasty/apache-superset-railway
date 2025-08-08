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
        SQLALCHEMY_ENGINE_OPTIONS = json.loads(engine_options)

# Redis configuration for caching
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    # Main cache configuration
    cache_config = os.environ.get("CACHE_CONFIG")
    if cache_config:
        CACHE_CONFIG = json.loads(cache_config)
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
        DATA_CACHE_CONFIG = json.loads(data_cache_config)
    
    # Filter state cache configuration
    filter_state_cache_config = os.environ.get("FILTER_STATE_CACHE_CONFIG")
    if filter_state_cache_config:
        FILTER_STATE_CACHE_CONFIG = json.loads(filter_state_cache_config)
    
    # Explore form data cache configuration
    explore_form_data_cache_config = os.environ.get("EXPLORE_FORM_DATA_CACHE_CONFIG")
    if explore_form_data_cache_config:
        EXPLORE_FORM_DATA_CACHE_CONFIG = json.loads(explore_form_data_cache_config)
    
    # Results backend configuration
    results_backend = os.environ.get("RESULTS_BACKEND")
    if results_backend:
        RESULTS_BACKEND = json.loads(results_backend)
    
    # Thumbnail cache configuration
    thumbnail_cache_config = os.environ.get("THUMBNAIL_CACHE_CONFIG")
    if thumbnail_cache_config:
        THUMBNAIL_CACHE_CONFIG = json.loads(thumbnail_cache_config)
    
    # Celery configuration
    celery_config = os.environ.get("CELERY_CONFIG")
    if celery_config:
        CELERY_CONFIG = json.loads(celery_config)
    
    # Rate limit storage
    ratelimit_storage_uri = os.environ.get("RATELIMIT_STORAGE_URI")
    if ratelimit_storage_uri:
        RATELIMIT_STORAGE_URI = ratelimit_storage_uri

# Mapbox configuration
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")

# Feature flags
feature_flags = os.environ.get("SUPERSET_FEATURE_FLAGS")
if feature_flags:
    FEATURE_FLAGS = json.loads(feature_flags)
else:
    FEATURE_FLAGS = {
        "ENABLE_TEMPLATE_PROCESSING": True,
        "ENABLE_JAVASCRIPT_CONTROLS": True
    }

# Security settings
ENABLE_PROXY_FIX = os.environ.get("ENABLE_PROXY_FIX", "True").lower() == "true"
TALISMAN_ENABLED = os.environ.get("TALISMAN_ENABLED", "False").lower() == "true"
WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "False").lower() == "true"
WTF_CSRF_EXEMPT_LIST = json.loads(os.environ.get("WTF_CSRF_EXEMPT_LIST", '["superset.views.api", "superset.views.core.api", "superset.charts.api.ChartRestApi.post"]'))

# CORS settings
ENABLE_CORS = os.environ.get("ENABLE_CORS", "True").lower() == "true"
cors_options = os.environ.get("CORS_OPTIONS")
if cors_options:
    CORS_OPTIONS = json.loads(cors_options)

# HTTP Headers
http_headers = os.environ.get("HTTP_HEADERS")
if http_headers:
    HTTP_HEADERS = json.loads(http_headers)

# Proxy configuration
proxy_fix_config = os.environ.get("PROXY_FIX_CONFIG")
if proxy_fix_config:
    PROXY_FIX_CONFIG = json.loads(proxy_fix_config)

# Query and row limits
ROW_LIMIT = int(os.environ.get("ROW_LIMIT", 50000))
VIZ_ROW_LIMIT = int(os.environ.get("VIZ_ROW_LIMIT", 10000))
SAMPLES_ROW_LIMIT = int(os.environ.get("SAMPLES_ROW_LIMIT", 1000))
FILTER_SELECT_ROW_LIMIT = int(os.environ.get("FILTER_SELECT_ROW_LIMIT", 10000))
SQL_MAX_ROW = int(os.environ.get("SQL_MAX_ROW", 100000))
DEFAULT_SQLLAB_LIMIT = int(os.environ.get("DEFAULT_SQLLAB_LIMIT", 1000))
SUPERSET_META_DB_LIMIT = int(os.environ.get("SUPERSET_META_DB_LIMIT", 1000))

# Timeouts
WEB_QUERY_TIMEOUT = int(os.environ.get("WEB_QUERY_TIMEOUT", 300))
DATABASE_QUERY_TIMEOUT = int(os.environ.get("DATABASE_QUERY_TIMEOUT", 60))
SUPERSET_WEBSERVER_TIMEOUT = int(os.environ.get("SUPERSET_WEBSERVER_TIMEOUT", 300))

# Async queries
GLOBAL_ASYNC_QUERIES = os.environ.get("GLOBAL_ASYNC_QUERIES", "True").lower() == "true"
SUPERSET_LOAD_CHART_ASYNC = os.environ.get("SUPERSET_LOAD_CHART_ASYNC", "True").lower() == "true"

# Webserver domains
superset_webserver_domains = os.environ.get("SUPERSET_WEBSERVER_DOMAINS")
if superset_webserver_domains:
    SUPERSET_WEBSERVER_DOMAINS = superset_webserver_domains.split(",")

# Session configuration
SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "None")
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
SESSION_COOKIE_HTTPONLY = os.environ.get("SESSION_COOKIE_HTTPONLY", "False").lower() == "true"

# Preferred URL scheme
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

# Public role configuration
AUTH_ROLE_PUBLIC = os.environ.get("AUTH_ROLE_PUBLIC", "Gamma")
PUBLIC_ROLE_LIKE = os.environ.get("PUBLIC_ROLE_LIKE", "Gamma")

# Disable some features that might cause issues in containerized environments
ENABLE_CHUNK_ENCODING = False

# Chart load configuration
CONCURRENT_CHART_LOAD_LIMIT = int(os.environ.get("CONCURRENT_CHART_LOAD_LIMIT", 4))

# Additional module DS map
additional_module_ds_map = os.environ.get("ADDITIONAL_MODULE_DS_MAP")
if additional_module_ds_map:
    ADDITIONAL_MODULE_DS_MAP = json.loads(additional_module_ds_map)

# Dashboard virtualization
DASHBOARD_VIRTUALIZATION = os.environ.get("DASHBOARD_VIRTUALIZATION", "False").lower() == "true"

# Preferred databases
preferred_databases = os.environ.get("PREFERRED_DATABASES")
if preferred_databases:
    PREFERRED_DATABASES = json.loads(preferred_databases)

# Other settings from environment
if os.environ.get("SUPERSET_UPDATE_PERMS"):
    SUPERSET_UPDATE_PERMS = int(os.environ.get("SUPERSET_UPDATE_PERMS"))

if os.environ.get("SUPERSET_LOAD_EXAMPLES"):
    SUPERSET_LOAD_EXAMPLES = int(os.environ.get("SUPERSET_LOAD_EXAMPLES"))
