web: gunicorn -w $UNICORN_N_WORKERS --timeout $UNICORN_TIMEOUT app:app
postdeploy: python scripts/pc.py install_postgres_extension &&
  alembic upgrade head &&
  python scripts/pc.py install_data
clock: python scripts/clock.py
redis-clock: python scripts/redis-clock.py