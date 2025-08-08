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
