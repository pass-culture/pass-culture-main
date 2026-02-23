#!/bin/bash

# Variabilize "bind" when we will merge dockerfiles. "127.0.0.1 for devs and 0.0.0.0 for kubernetes"
exec gunicorn \
    --preload \
    --bind 0.0.0.0:$GUNICORN_PORT \
    --worker-class gthread \
    --max-requests $GUNICORN_MAX_REQUESTS \
    --max-requests-jitter $GUNICORN_MAX_REQUESTS_JITTER \
    --workers $GUNICORN_WORKERS \
    --threads $GUNICORN_THREADS \
    --timeout $GUNICORN_TIMEOUT \
    --graceful-timeout $GUNICORN_GRACEFUL_TIMEOUT \
    --keep-alive $GUNICORN_KEEP_ALIVE \
    --log-level $GUNICORN_LOG_LEVEL \
    --config gunicorn.conf.py \
    ${GUNICORN_FLASK_APP:-pcapi.app:app}
