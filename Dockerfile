FROM apache/superset:latest

USER root

# Install system packages needed for MySQL & psycopg2
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python drivers
RUN pip install mysqlclient psycopg2 pymysql

# Install extra Python packages if any
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: pass environment variables from Railway or your .env
ENV ADMIN_USERNAME=admin
ENV ADMIN_EMAIL=admin@example.com
ENV ADMIN_PASSWORD=admin
ENV SECRET_KEY="my_superset_secret_key"
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# Copy startup and config scripts
COPY config/superset_init.sh /app/superset_init.sh
COPY config/superset_config.py /app/superset_config.py

RUN chmod +x /app/superset_init.sh

USER superset

ENV CACHE_BUSTER=20250617A

# Start using the init script
CMD ["/app/superset_init.sh"]
