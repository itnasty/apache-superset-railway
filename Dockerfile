FROM apache/superset:latest

USER root

# Install system dependencies including PostgreSQL development libraries
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for SQLite fallback and set permissions
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# The Apache Superset base image has Python and pip, but the virtual environment
# is created later. We need to install psycopg2-binary in the system Python first
RUN pip install --no-cache-dir psycopg2-binary==2.9.9 && \
    pip install --no-cache-dir -r /app/requirements.txt

# If virtual environment exists, also install there
RUN if [ -d "/app/.venv" ]; then \
        /app/.venv/bin/pip install --no-cache-dir psycopg2-binary==2.9.9 && \
        /app/.venv/bin/pip install --no-cache-dir -r /app/requirements.txt; \
    fi

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/superset_init.sh /app/superset_init.sh
RUN chmod +x /app/superset_init.sh

# Set ownership of app directory to superset user
RUN chown -R superset:superset /app

# Only set the config path - Railway provides all other environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
