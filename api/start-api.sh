#!/bin/bash
set -e

echo >&2 -e "\n\033[0;32mInstall app\n"
flask install_postgres_extensions

echo >&2 -e "\n\033[0;32mRun migrations\n"
alembic upgrade pre@head
alembic upgrade post@head

echo >&2 -e "\n\033[0;32mInstall feature flags\n"
flask install_data

echo >&2 -e "\n\033[0;32mStart app\n"
python src/pcapi/app.py
