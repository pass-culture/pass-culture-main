web: python app.py
postdeploy: alembic upgrade head && python scripts/pc.py install_data
clock: python scripts/clock.py