#!/bin/bash


# GET ANONYMIZE PWD
if [[ $# -gt 1 ]] && [[ "$1" == "-p" ]]; then
  DATABASE_ANONYMIZED_PWD=$2
  shift 2
fi

if [[ ! -z "$DATABASE_ANONYMIZED_PWD" ]]; then
  password="$DATABASE_ANONYMIZED_PWD"
else
  echo "You must set the DATABASE_ANONYMIZED_PWD env variable in order to run the script."
  exit 1
fi

if [[ -z "$APP_NAME" ]]; then
  echo "Connect to local database"
  cat anonymize.sql | sed -e "s/##PASSWORD##/$password/" | docker exec -i `docker ps | grep postgres | cut -d" " -f 1` psql -d pass_culture -U pass_culture
else
  echo "Connect to env database"
  PGPASSWORD="$PG_PASSWORD" psql --host 127.0.0.1 \
                               --port 10000 \
                               --username "$PG_USER" \
                               --dbname "$PG_USER" \
                               -a -f anonymise.sql
fi
