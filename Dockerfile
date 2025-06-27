FROM apache/superset:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for SQLite fallback and set permissions
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Activate virtual environment and install packages
RUN . /app/.venv/bin/activate && pip install --no-cache-dir -r /app/requirements.txt

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
