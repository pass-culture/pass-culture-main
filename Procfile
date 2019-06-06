web: gunicorn -w $UNICORN_N_WORKERS --timeout $UNICORN_TIMEOUT app:app
postdeploy: alembic upgrade head && python scripts/pc.py install_data
clock: python scripts/clock.py