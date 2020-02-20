web: gunicorn -w $UNICORN_N_WORKERS --timeout $UNICORN_TIMEOUT app:app
postdeploy: python scripts/pc.py install_postgres_extension &&
  alembic upgrade head &&
  python scripts/pc.py install_data
clock: python scheduled_tasks/clock.py
algoliaclock: python scheduled_tasks/algolia_clock.py
titeliveclock: python scheduled_tasks/titelive_clock.py