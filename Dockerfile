FROM apache/superset:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is available in the venv and install ALL database drivers
# pymysql - required for MySQL connections
# mysqlclient - alternative MySQL driver
# psycopg2-binary - required for PostgreSQL connections
RUN python3 -m ensurepip --default-pip || true && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir pymysql mysqlclient psycopg2-binary

ENV ADMIN_USERNAME $ADMIN_USERNAME
ENV ADMIN_EMAIL $ADMIN_EMAIL
ENV ADMIN_PASSWORD $ADMIN_PASSWORD

COPY /config/superset_init.sh ./superset_init.sh
RUN chmod +x ./superset_init.sh

COPY /config/superset_config.py /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py
ENV SECRET_KEY $SECRET_KEY

USER superset

ENTRYPOINT [ "./superset_init.sh" ]
