#!/bin/bash
set -e

until psql $DATABASE_URL -c '\q'; do
  echo >&2 -e "\033[0;33mPostgres is unavailable - sleeping"
  sleep 1
done

echo >&2 -e "\n\033[0;32mPostgres is up - Install app\n"
flask install_postgres_extensions

echo >&2 -e "\n\033[0;32mPostgres is up - Running migration\n"
alembic upgrade pre@head
alembic upgrade post@head

echo >&2 -e "\n\033[0;32mMigrations have run - Installing feature flags\n"
flask install_data

echo >&2 -e "\n\033[0;32mFeature flags installed - Starting the application\n"
while true; do python src/pcapi/app.py || continue; done
