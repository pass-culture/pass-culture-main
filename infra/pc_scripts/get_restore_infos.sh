#!/bin/bash

function get_restore_infos {
  if [[ "$ENV" == "development" ]]; then
      echo "Restore infos are not available in development environment"
      exit
  else
      echo "select * from db_restore_infos; \q" | scalingo -a $SCALINGO_APP pgsql-console | tail -n 5
      exit
  fi
}
