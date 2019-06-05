web: gunicorn -w 5 app:app
postdeploy: alembic upgrade head && python scripts/pc.py install_data
clock: python scripts/clock.py