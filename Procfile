web: gunicorn -w $N_UNICORN_WORKERS app:app
postdeploy: alembic upgrade head && python scripts/pc.py install_data
clock: python scripts/clock.py