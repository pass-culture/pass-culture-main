#!/bin/bash

# Variabilize "bind" when we will merge dockerfiles. "127.0.0.1 for devs and 0.0.0.0 for kubernetes"
gunicorn \
    --preload \
    --bind 0.0.0.0:$GUNICORN_PORT \
    --worker-class gthread \
    --max-requests $GUNICORN_MAX_REQUESTS \
    --max-requests-jitter $GUNICORN_MAX_REQUESTS_JITTER \
    --workers $GUNICORN_WORKERS \
    --threads $GUNICORN_THREADS \
    --timeout $GUNICORN_TIMEOUT \
    --log-level debug \
    pcapi.app:app
