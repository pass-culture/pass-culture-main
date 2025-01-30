#!/bin/bash
set -e

until psql $DATABASE_URL -c '\q'; do
  echo >&2 -e "\033[0;33mPostgres is unavailable - sleeping"
  sleep 1
done

celery -A pcapi.celery_tasks.celery_worker worker -Q mails

