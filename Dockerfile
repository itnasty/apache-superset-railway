FROM apache/superset:4.0.2

# Switch to root to install packages
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python packages directly (no venv needed in this image)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Verify installations
RUN python -c "import psycopg2; print('✓ psycopg2 installed')" && \
    python -c "import gevent; print('✓ gevent installed')" && \
    python -c "import pymysql; print('✓ pymysql installed')" && \
    python -c "import redis; print('✓ redis installed')"

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/cache_timeout_patch.py /app/
COPY config/apply_patch.py /app/
COPY config/superset_init.sh /app/
COPY gunicorn_config.py /app/

# Make scripts executable
RUN chmod +x /app/superset_init.sh /app/apply_patch.py

# Copy additional scripts
COPY scripts/cache_warmer.py /app/scripts/
COPY scripts/cache_warmer_enhanced.py /app/scripts/
COPY scripts/superset-cron /app/scripts/
RUN chmod +x /app/scripts/cache_warmer.py /app/scripts/cache_warmer_enhanced.py

# Copy test script
COPY config/test_redis_endpoint.py /app/pythonpath/

# Set proper ownership
RUN chown -R superset:superset /app

# Switch back to superset user
USER superset

# Set working directory
WORKDIR /app

# Set Python path
ENV PYTHONPATH="/app/pythonpath:${PYTHONPATH}"
ENV SUPERSET_CONFIG_PATH="/app/superset_config.py"

# Expose port
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1

# Start command
CMD ["/app/superset_init.sh"]
