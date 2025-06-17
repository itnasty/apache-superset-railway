FROM apache/superset:latest

USER root

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python drivers (native + pymysql)
RUN pip install mysqlclient psycopg2

# Add requirements.txt and install additional Python packages (like pymysql)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV ADMIN_USERNAME $ADMIN_USERNAME
ENV ADMIN_EMAIL $ADMIN_EMAIL
ENV ADMIN_PASSWORD $ADMIN_PASSWORD
ENV DATABASE $DATABASE

COPY /config/superset_init.sh ./superset_init.sh
RUN chmod +x ./superset_init.sh

COPY /config/superset_config.py /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py
ENV SECRET_KEY $SECRET_KEY

USER superset

ENTRYPOINT [ "./superset_init.sh" ]
