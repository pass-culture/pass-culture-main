#!/bin/bash

function access_db_logs() {
  if [[ "$ENV" == "development" ]]; then
    export RUN="docker exec pc-postgres bash -c 'tail -f /var/lib/postgresql/data/log/postgresql-*'"
  else
    echo "Use GCP console or gcloud CLI to access cloudsql_database logs"
    exit
  fi
}
