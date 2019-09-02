#!/bin/bash

function access_db_logs {
  if [[ "$ENV" == "development" ]]; then
      RUN="docker exec pc-postgres bash -c 'tail -f /var/lib/postgresql/data/log/*'"
  else
      local postgres_addon_id=$(scalingo --app $SCALINGO_APP addons |grep PostgreSQL | cut -d' ' -f 4)
      echo $postgres_addon_id $SCALINGO_APP
      RUN="scalingo --app $SCALINGO_APP logs --addon $postgres_addon_id -f -n 5"
  fi
}