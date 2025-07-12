import os

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY", "")

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

SECRET_KEY = os.environ.get("SECRET_KEY", "your-default-secret-key")

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:////app/data/superset.db"

SQLALCHEMY_DATABASE_URI = DATABASE_URL

if DATABASE_URL.startswith("sqlite://"):
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"check_same_thread": False}
    }

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': REDIS_URL
    }

TALISMAN_ENABLED = True
WTF_CSRF_ENABLED = True
ENABLE_PROXY_FIX = True
ENABLE_CHUNK_ENCODING = False
