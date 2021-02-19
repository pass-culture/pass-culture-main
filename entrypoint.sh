#!/bin/bash

gunicorn \
    --preload \
    $GUNICORN_BIND_ARG \
    --workers 1 \
    --threads 4 \
    --timeout 0 \
    --access-logformat '{"request_id":"%({X-Request-Id}i)s",\
                        "response_code":"%(s)s","request_method":"%(m)s",\
                        "request_path":"%(U)s","request_querystring":"%(q)s",\
                        "request_duration":"%(D)s","response_length":"%(B)s", \
                        "from":"gunicorn"}' \
    pcapi.app:app
