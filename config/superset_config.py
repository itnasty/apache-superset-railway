import os
from urllib.parse import urlparse
from datetime import timedelta

# We'll apply the cache timeout patch after Flask app initialization
# The patch will be loaded by superset_init.sh or when the app starts

# Flask App Config
ROW_LIMIT = 15000  # Reduced from 25K to avoid packet sequence errors
SUPERSET_WEBSERVER_TIMEOUT = 900  # 15 minutes
SUPERSET_ROW_LIMIT = 15000  # Explicit superset row limit
SECRET_KEY = os.environ.get("SECRET_KEY", "ThisIsNotSecureChangeIt123")

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE") or os.environ.get("DATABASE_URL", "sqlite:////app/data/superset.db")
SQLALCHEMY_DATABASE_URI = DATABASE_URL

# Database Connection Pool Optimization
SQLALCHEMY_POOL_SIZE = 10  # Reduced from 20 to avoid connection overload
SQLALCHEMY_POOL_RECYCLE = 300  # Recycle connections every 5 minutes (was 3600)
SQLALCHEMY_MAX_OVERFLOW = 20  # Reduced from 40
SQLALCHEMY_POOL_PRE_PING = True  # Test connections before using them
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # Verify connection before use
    "pool_recycle": 300,  # Recycle every 5 minutes
    "echo": False,  # Set to True for debugging
    "echo_pool": False,  # Set to True to debug connection pool
}

# Redis Configuration for Advanced Caching
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    redis_parsed = urlparse(REDIS_URL)
    
    # 1. Results Backend - Query Results Cache (1 hour)
    # RESULTS_BACKEND requires a cachelib object, not a dictionary configuration
    from flask_caching.backends.rediscache import RedisCache
    RESULTS_BACKEND = RedisCache(
        host=redis_parsed.hostname,
        port=redis_parsed.port or 6379,
        password=redis_parsed.password,
        db=0,
        key_prefix='superset_results_',
        default_timeout=3600  # 1 hour for query results
    )
    
    # 2. Data Cache - Dashboard/Chart Data (24 hours)
    DATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_data_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 1,
    }
    
    # Force cache timeouts (override Superset defaults)
    CACHE_DEFAULT_TIMEOUT = 86400  # 24 hours global default
    DATA_CACHE_TIMEOUT = 86400  # Explicit data cache timeout
    DASHBOARD_CACHE_TIMEOUT = 86400  # Dashboard cache timeout
    CHART_CACHE_TIMEOUT = 86400  # Chart cache timeout
    EXPLORE_CACHE_TIMEOUT = 7200  # Explore form timeout
    
    # Override chart data API cache timeout (Superset hardcoded default is 600)
    DEFAULT_CACHE_CONFIG = DATA_CACHE_CONFIG  # Use same config as data cache
    CHART_DATA_CACHE_TIMEOUT = 86400  # 24 hours for chart data API
    
    # Try to override the 600-second default
    import os
    os.environ['DATA_CACHE_TIMEOUT'] = '86400'
    os.environ['CHART_DATA_CACHE_TIMEOUT'] = '86400'
    
    # 3. Filter State Cache (24 hours)
    FILTER_STATE_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_filter_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 2,
    }
    
    # 4. Explore Form Data Cache (2 hours)
    EXPLORE_FORM_DATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 7200,  # 2 hours
        "CACHE_KEY_PREFIX": "superset_explore_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 3,
    }
    
    # 5. Thumbnail Cache (7 days) - NEW
    THUMBNAIL_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 604800,  # 7 days for thumbnails
        "CACHE_KEY_PREFIX": "superset_thumb_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 4,
    }
    
    # 6. Metadata Cache (24 hours) - NEW
    METADATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
        "CACHE_KEY_PREFIX": "superset_meta_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 5,
    }
    
    # General cache config
    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours (was 5 minutes)
        "CACHE_KEY_PREFIX": "superset_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 6,
    }

# Railway-Specific: Careful with async operations
GLOBAL_ASYNC_QUERIES = False
SUPERSET_LOAD_CHART_ASYNC = False

# Force chart data cache timeout (override Superset's 600-second default)
CHART_CACHE_DEFAULT_TIMEOUT = 86400  # 24 hours
DEFAULT_CACHE_TIMEOUT = 86400  # 24 hours for all caches
SUPERSET_DEFAULT_CACHE_TIMEOUT_SECONDS = 86400  # Another possible key

# Slightly increase concurrent loading (test carefully on Railway)
CONCURRENT_CHART_LOAD_LIMIT = 2  # Increased from 1 to 2

# Dashboard virtualization for better performance
DASHBOARD_VIRTUALIZATION = True
DASHBOARD_VIRTUALIZATION_LIMIT = 10

# CORS Configuration
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "origins": ["*"]
}

# Session Configuration
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# Performance Feature Flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_VIRTUALIZATION": True,  # Virtual scrolling
    "DASHBOARD_NATIVE_FILTERS": True,  # Faster filters
    "DASHBOARD_CROSS_FILTERS": True,  # Cross-filtering
    # "THUMBNAILS": True,  # Disabled - requires Selenium/Chrome
    # "THUMBNAILS_SQLA_LISTENERS": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": True,  # Card view for lists
    "ENABLE_EXPLORE_DRAG_AND_DROP": True,
    "DISABLE_LEGACY_DATASOURCE_EDITOR": True,
    "VERSIONED_EXPORT": True,
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
}

# Railway proxy configuration
ENABLE_PROXY_FIX = True
PREFERRED_URL_SCHEME = "https"

# Optimized Timeouts
DATABASE_QUERY_TIMEOUT = 300  # 5 minutes
WEB_QUERY_TIMEOUT = 900  # 15 minutes
SQLLAB_TIMEOUT = 900  # 15 minutes
SQLLAB_ASYNC_TIME_LIMIT_SEC = 900

# Database Connection Testing Timeout (fixes 422 errors for high-latency connections)
# This MUST be a timedelta object, not an integer!
# Used by func_timeout wrapper in test_connection.py
TEST_DATABASE_CONNECTION_TIMEOUT = timedelta(seconds=120)  # 2 minutes (increased from default 30s)

# Query limits
SQL_MAX_ROW = 50000  # Reduced from 100K to avoid connection issues
SAMPLES_ROW_LIMIT = 1000  # Sample data limit (keep low for fast previews)
FILTER_SELECT_ROW_LIMIT = 10000  # Filter dropdown limit
DISPLAY_MAX_ROW = 15000  # Maximum rows to display in table visualization

# Compression
COMPRESS_REGISTER = True
COMPRESS_MIN_SIZE = 500

# Static file caching
SEND_FILE_MAX_AGE_DEFAULT = 604800  # 7 days

# Performance logging (disabled to avoid configuration issues)
# STATS_LOGGER = False  # Uncomment to enable
# EVENT_LOGGER = False  # Uncomment to enable

# Thumbnail generation user
THUMBNAIL_SELENIUM_USER = os.environ.get("ADMIN_USERNAME", "admin")

# Cache key factory (includes more context)
def make_cache_key(*args, **kwargs):
    """Create cache key with user context"""
    from flask import request, g
    
    path = request.path
    args_str = str(hash(frozenset(request.args.items())))
    user_id = getattr(g, 'user', {}).get('id', 'anonymous')
    
    return f"{user_id}:{path}:{args_str}"

CACHE_KEY_FACTORY = make_cache_key

# Alert & Report Configuration (if using)
ALERT_REPORTS_WORKING_TIME_OUT_KILL = True
ALERT_REPORTS_WORKING_TIME_OUT_LAG = 60
ALERT_REPORTS_QUERY_EXECUTION_MAX_TRIES = 3

# CSV Upload limits
CSV_UPLOAD_MAX_SIZE = 104857600  # 100MB

# SQL Lab Configuration
SQLLAB_QUERY_COST_ESTIMATE = True  # Show query cost
SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT = 10  # Timeout for estimates
SQLLAB_VALIDATION_TIMEOUT = 10  # Query validation timeout

# Enable query cost estimation for optimization
ESTIMATE_QUERY_COST = True

# Prevent CSRF issues with charts/dashboards
WTF_CSRF_EXEMPT_LIST = [
    'superset.charts.api.data',
    'superset.charts.data.api.get_data',
    'superset.dashboards.api.get_datasets',
    'superset.dashboards.api.get_charts',
    'superset.explore.form_data.api',
]

print("🚀 Optimized Superset configuration loaded with advanced caching!")