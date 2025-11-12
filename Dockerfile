FROM apache/superset:latest

USER root

# Install dependencies including cron for cache warming
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements
COPY requirements.txt /app/

# Install packages directly into the venv using system pip
# This forces packages into /app/.venv/lib/python3.10/site-packages/
RUN python3 -m pip install --no-cache-dir --target=/app/.venv/lib/python3.10/site-packages -r /app/requirements.txt

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/cache_timeout_patch.py /app/
COPY config/apply_patch.py /app/
COPY config/superset_init.sh /app/
COPY gunicorn_config.py /app/
RUN chmod +x /app/superset_init.sh /app/apply_patch.py

# Copy cache warmer and performance scripts
COPY scripts/cache_warmer.py /app/scripts/
COPY scripts/cache_warmer_enhanced.py /app/scripts/
COPY scripts/superset-cron /app/scripts/
RUN chmod +x /app/scripts/cache_warmer.py /app/scripts/cache_warmer_enhanced.py

# Copy test endpoint (optional for monitoring)
COPY config/test_redis_endpoint.py /app/pythonpath/

# Set ownership
RUN chown -R superset:superset /app

# Environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV PYTHONPATH=/app:$PYTHONPATH

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
