FROM apache/superset:latest

USER root

# Install system dependencies for building database drivers
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install database drivers in venv (pymysql, mysqlclient, psycopg2-binary)
RUN python3 -m ensurepip --default-pip || true && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir pymysql mysqlclient psycopg2-binary flask-cors

# Copy initialization script and config
COPY /config/superset_init.sh ./superset_init.sh
RUN chmod +x ./superset_init.sh

COPY /config/superset_config.py /app/

USER superset

CMD ["./superset_init.sh"]
