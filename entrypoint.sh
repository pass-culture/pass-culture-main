#!/bin/bash
set -e

python src/pcapi/scripts/pc.py install_data && python src/pcapi/scripts/pc.py install_postgres_extension && alembic upgrade head

gunicorn \
    --preload \
    --workers 1 \
    --threads 4 \
    --timeout 0 \
    --access-logformat '{"request_id":"%({X-Request-Id}i)s",\
                        "response_code":"%(s)s","request_method":"%(m)s",\
                        "request_path":"%(U)s","request_querystring":"%(q)s",\
                        "request_duration":"%(D)s","response_length":"%(B)s", \
                        "from":"gunicorn"}' \
    pcapi.app:app
