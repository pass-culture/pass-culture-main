#!/bin/bash

# Variabilize "bind" when we will merge dockerfiles. "127.0.0.1 for devs and 0.0.0.0 for kubernetes"
env
gunicorn \
    --preload \
    --bind 0.0.0.0:${GUNICORN_PORT:-5000} \
    --worker-class ${GUNICORN_WORKER_CLASS:-gthread} \
    --max-requests ${GUNICORN_MAX_REQUESTS:-0} \
    --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-0} \
    --workers ${GUNICORN_WORKERS:-1} \
    --threads ${GUNICORN_THREADS:-1} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --log-level ${GUNICORN_LOG_LEVEL:-info} \
    pcapi.app:app
