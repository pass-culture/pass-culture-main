web: gunicorn -w $UNICORN_N_WORKERS --timeout $UNICORN_TIMEOUT --access-logformat  '{"request_id":"%({X-Request-Id}i)s","response_code":"%(s)s","request_method":"%(m)s","request_path":"%(U)s","request_querystring":"%(q)s","request_timetaken":"%(M)s","response_length":"%(B)s", "from":"gunicorn"}' app:app
postdeploy: python scripts/pc.py install_postgres_extension &&
  alembic upgrade head &&
  python scripts/pc.py install_data
clock: python scheduled_tasks/clock.py
algoliaclock: python scheduled_tasks/algolia_clock.py
titeliveclock: python scheduled_tasks/titelive_clock.py
worker: python workers/worker.py
