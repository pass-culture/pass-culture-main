#!/bin/bash

export ENABLE_FLASK_PROMETHEUS_EXPORTER="${ENABLE_FLASK_PROMETHEUS_EXPORTER:-1}"
export FLASK_PROMETHEUS_EXPORTER_PORT="${FLASK_PROMETHEUS_EXPORTER_PORT:-5010}"
export PROMETHEUS_MULTIPROC_DIR="${PROMETHEUS_MULTIPROC_DIR:-/tmp}"
export FLASK_ENTRYPOINT="${FLASK_ENTRYPOINT:-src/pcapi/app.py}"
if [ "${FLASK_SERVER:-0}" = "1" ]; then
  until psql "${DATABASE_URL:-postgres}" -c '\q'; do
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
  while true; do python $FLASK_ENTRYPOINT || continue; done
else
  # Variabilize "bind" when we will merge dockerfiles. "127.0.0.1 for devs and 0.0.0.0 for kubernetes"
  exec gunicorn \
      --preload \
      --bind 0.0.0.0:${GUNICORN_PORT:-5000} \
      --worker-class gthread \
      --max-requests ${GUNICORN_MAX_REQUESTS:-0} \
      --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-0} \
      --workers ${GUNICORN_WORKERS:-2} \
      --threads ${GUNICORN_THREADS:-5} \
      --timeout ${GUNICORN_TIMEOUT:-90} \
      --log-level ${GUNICORN_LOG_LEVEL:-info} \
      --config gunicorn.conf.py \
      ${GUNICORN_FLASK_APP:-pcapi.app:app}
fi
