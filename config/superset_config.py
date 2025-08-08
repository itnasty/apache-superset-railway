import os

# Flask App Config
ROW_LIMIT = 50000
SUPERSET_WEBSERVER_TIMEOUT = 300
SECRET_KEY = os.environ.get("SECRET_KEY", "USE_YOUR_OWN_SECURE_RANDOM_KEY")

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False

# Database
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:////app/data/superset.db")

# Async queries
GLOBAL_ASYNC_QUERIES = os.environ.get("GLOBAL_ASYNC_QUERIES", "false").lower() == "true"

# Chart loading
CONCURRENT_CHART_LOAD_LIMIT = int(os.environ.get("CONCURRENT_CHART_LOAD_LIMIT", 4))

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

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# For Railway
ENABLE_PROXY_FIX = True
PREFERRED_URL_SCHEME = "https"
