#!/bin/bash
set -e

# API waits for database, runs migrations and initialize data
echo >&2 -e "\033[0;33mWaiting until API is available"
until curl "http://flask:5001/health/api" --silent --output nul; do
  sleep 2
done

echo >&2 -e "\n\033[0;32mAPI is up - Starting backoffice application\n"
while true; do python src/pcapi/backoffice_app.py || continue; done
