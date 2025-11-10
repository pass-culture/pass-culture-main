#!/bin/bash
set -e

until psql $DATABASE_URL -c '\q'; do
  echo >&2 -e "\033[0;33mPostgres is unavailable - sleeping"
  sleep 1
done

export PROMETHEUS_MULTIPROC_DIR="/tmp/prometheus"
mkdir -p $PROMETHEUS_MULTIPROC_DIR
celery -A pcapi.celery_tasks.celery_worker worker \
  -Q "celery.external_calls.priority,celery.internal_calls.priority,celery.internal_calls.default,celery.external_calls.default" \
  --loglevel=INFO
