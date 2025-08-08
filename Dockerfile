FROM apache/superset:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for SQLite fallback
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements first
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/superset_init.sh /app/superset_init.sh
RUN chmod +x /app/superset_init.sh

# Set ownership
RUN chown -R superset:superset /app

# Set environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
