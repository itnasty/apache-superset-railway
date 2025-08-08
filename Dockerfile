FROM apache/superset:latest

USER root

# Install system dependencies including network debugging tools
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    wget \
    netcat \
    telnet \
    dnsutils \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for SQLite fallback and set permissions
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python packages system-wide
RUN pip install --no-cache-dir psycopg2-binary==2.9.9 && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/superset_init.sh /app/superset_init.sh
RUN chmod +x /app/superset_init.sh

# Copy diagnostic script
COPY diagnose_dashboard_issues.py /app/diagnose_dashboard_issues.py

# Set ownership of app directory to superset user
RUN chown -R superset:superset /app

# Install additional packages for debugging
RUN pip install --no-cache-dir httpie requests

# Only set the config path - Railway provides all other environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH
ENV FLASK_ENV=development

USER superset

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8088}/health || exit 1

CMD ["/bin/bash", "/app/superset_init.sh"]
