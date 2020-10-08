web: gunicorn -w $UNICORN_N_WORKERS --timeout $UNICORN_TIMEOUT --access-logformat  '{"request_id":"%({X-Request-Id}i)s","response_code":%(s)s,"request_method":"%(m)s","request_path":"%(U)s","request_querystring":"%(q)s","request_duration":%(D)s,"response_length":%(B)s, "from":"gunicorn"}' pcapi.app:app
postdeploy: python src/pcapi/scripts/pc.py install_postgres_extension && alembic upgrade head && python src/pcapi/scripts/pc.py install_data
clock: python src/pcapi/scheduled_tasks/clock.py
algoliaclock: python src/pcapi/scheduled_tasks/algolia_clock.py
titeliveclock: python src/pcapi/scheduled_tasks/titelive_clock.py
worker: python src/pcapi/workers/worker.py
