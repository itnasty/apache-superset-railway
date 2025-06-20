FROM apache/superset:latest

USER root

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install mysqlclient psycopg2 pymysql

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt || true

COPY config/superset_config.py /app/
COPY config/superset_init.sh /app/superset_init.sh
RUN chmod +x /app/superset_init.sh

ENV ADMIN_USERNAME=admin
ENV ADMIN_EMAIL=admin@example.com
ENV ADMIN_PASSWORD=admin
ENV SECRET_KEY=mysecretkey
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
