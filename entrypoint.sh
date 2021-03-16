#!/bin/bash

# Variabilize "bind" when we will merge dockerfiles. "127.0.0.1 for devs and 0.0.0.0 for kubernetes"
gunicorn \
    --preload \
    --bind 0.0.0.0:$GUNICORN_PORT \
    --workers $GUNICORN_WORKERS \
    --threads $GUNICORN_THREADS \
    --timeout $GUNICORN_TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --access-logformat '{"request_id":"%({X-Request-Id}i)s","response_code":%(s)s,"request_method":"%(m)s","request_path":"%(U)s","request_querystring":"%(q)s","request_duration":%(D)s,"response_length":%(B)s, "from":"gunicorn"}' \
    pcapi.app:app
