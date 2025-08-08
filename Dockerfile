FROM apache/superset:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/data && chown -R superset:superset /app/data

# Copy requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy configuration files
COPY config/superset_config.py /app/
COPY config/superset_init.sh /app/
RUN chmod +x /app/superset_init.sh

# Set ownership
RUN chown -R superset:superset /app

# Environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
