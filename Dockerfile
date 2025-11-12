FROM apache/superset:latest

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/data && chown -R superset:superset /app/data

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY config/superset_config.py /app/
COPY config/cache_timeout_patch.py /app/
COPY config/apply_patch.py /app/
COPY config/superset_init.sh /app/
COPY gunicorn_config.py /app/
RUN chmod +x /app/superset_init.sh /app/apply_patch.py

COPY scripts/cache_warmer.py /app/scripts/
COPY scripts/cache_warmer_enhanced.py /app/scripts/
COPY scripts/superset-cron /app/scripts/
RUN chmod +x /app/scripts/cache_warmer.py /app/scripts/cache_warmer_enhanced.py

COPY config/test_redis_endpoint.py /app/pythonpath/

RUN chown -R superset:superset /app

ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV PYTHONPATH=/app:$PYTHONPATH

USER superset

CMD ["/bin/bash", "/app/superset_init.sh"]
