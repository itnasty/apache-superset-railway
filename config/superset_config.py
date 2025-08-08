import os

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "CoFEz4QHYKlnX4F7eoknGg0vxb6dA6DV")

# Database configuration
DATABASE_URL = os.environ.get("DATABASE") or os.environ.get("DATABASE_URL", "sqlite:////app/data/superset.db")
SQLALCHEMY_DATABASE_URI = DATABASE_URL

# Basic configuration
ROW_LIMIT = 50000
SUPERSET_WEBSERVER_TIMEOUT = 600

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Disable CSRF for API
WTF_CSRF_ENABLED = False

# Enable CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "origins": ["*"]
}

# For Railway proxy
ENABLE_PROXY_FIX = True

# Session configuration
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# Set async queries based on environment variable
GLOBAL_ASYNC_QUERIES = os.environ.get("GLOBAL_ASYNC_QUERIES", "False").lower() == "true"

# Concurrent chart load limit
CONCURRENT_CHART_LOAD_LIMIT = int(os.environ.get("CONCURRENT_CHART_LOAD_LIMIT", 1))
