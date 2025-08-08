"""
Optimized Superset Configuration for High Volume Sales Data
This configuration balances performance with data completeness
"""

import os
from urllib.parse import urlparse

# =============================================================================
# ROW LIMITS - Optimized for High Volume Sales Data
# =============================================================================

# Dashboard/Chart Row Limits (what users see in visualizations)
ROW_LIMIT = 25000  # Increased for sales dashboards, but not too high
                    # Good for: Daily/weekly sales summaries
                    # Impact: 3-5 second queries, manageable cache

# SQL Lab Limits (for data exploration and ad-hoc queries)
SQL_MAX_ROW = 100000  # Higher limit for data analysis
                       # Good for: Monthly/quarterly reports
                       # Impact: Available for power users who need it

# Sample/Preview Limits (for quick data inspection)
SAMPLES_ROW_LIMIT = 1000  # Keep low for fast previews
FILTER_SELECT_ROW_LIMIT = 10000  # Dropdown filters stay responsive

# =============================================================================
# SMART DATA STRATEGIES FOR HIGH VOLUME
# =============================================================================

# 1. USE AGGREGATE TABLES
# Instead of querying raw sales:
#   CREATE MATERIALIZED VIEW sales_daily AS
#   SELECT date, SUM(amount) as total, COUNT(*) as transactions
#   FROM sales GROUP BY date;

# 2. TIME-BASED PARTITIONING
# Query only recent data by default:
DEFAULT_TIME_FILTER = "last_90_days"  # Add to your datasets

# 3. QUERY OPTIMIZATION
DATABASE_QUERY_TIMEOUT = 300  # 5 minutes for complex queries
WEB_QUERY_TIMEOUT = 900  # 15 minutes max

# Enable query cost estimation to warn users
SQLLAB_QUERY_COST_ESTIMATE = True
ESTIMATE_QUERY_COST = True

# =============================================================================
# CACHING STRATEGY FOR LARGE DATASETS
# =============================================================================

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    redis_parsed = urlparse(REDIS_URL)
    
    # Longer cache for aggregated data (since it changes less frequently)
    DATA_CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 172800,  # 48 hours for sales summaries
        "CACHE_KEY_PREFIX": "superset_data_",
        "CACHE_REDIS_HOST": redis_parsed.hostname,
        "CACHE_REDIS_PORT": redis_parsed.port or 6379,
        "CACHE_REDIS_PASSWORD": redis_parsed.password,
        "CACHE_REDIS_DB": 1,
    }
    
    # Results cache for expensive queries
    RESULTS_BACKEND = {
        "cache_type": "RedisCache",
        "cache_redis_host": redis_parsed.hostname,
        "cache_redis_port": redis_parsed.port or 6379,
        "cache_redis_password": redis_parsed.password,
        "cache_redis_db": 0,
        "cache_key_prefix": "superset_results_",
        "cache_default_timeout": 7200,  # 2 hours for query results
    }

# =============================================================================
# PERFORMANCE FEATURES FOR LARGE DATA
# =============================================================================

# Pagination for large result sets
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_VIRTUALIZATION": True,  # Critical for many charts
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": True,
    
    # Enable data pagination (NEW)
    "ENABLE_PAGINATION": True,
    "SAMPLES_ROW_PAGINATION": True,
    
    # Query improvements
    "ENABLE_QUERY_COST_ESTIMATION": True,
    "ENABLE_SQL_VALIDATOR_ESTIMATES": True,
}

# Async queries for large datasets (if Railway supports it)
# GLOBAL_ASYNC_QUERIES = True  # Only if you have Celery workers

# =============================================================================
# DATABASE OPTIMIZATIONS
# =============================================================================

# Larger connection pool for concurrent queries
SQLALCHEMY_POOL_SIZE = 30  # Increased from 20
SQLALCHEMY_MAX_OVERFLOW = 60  # Increased from 40
SQLALCHEMY_POOL_RECYCLE = 1800  # 30 minutes

# =============================================================================
# RAILWAY-SPECIFIC SETTINGS
# =============================================================================

# Keep these for Railway compatibility
GLOBAL_ASYNC_QUERIES = False
SUPERSET_LOAD_CHART_ASYNC = False
CONCURRENT_CHART_LOAD_LIMIT = 2  # Can try 3 if stable

# Other settings remain the same...
SUPERSET_WEBSERVER_TIMEOUT = 900
SECRET_KEY = os.environ.get("SECRET_KEY", "ThisIsNotSecureChangeIt123")
WTF_CSRF_ENABLED = False
ENABLE_CORS = True
ENABLE_PROXY_FIX = True
PREFERRED_URL_SCHEME = "https"

print("🚀 High-volume data configuration loaded!")