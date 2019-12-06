#!/bin/bash

# GET ANONYMIZE PWD
if [[ $# -gt 1 ]] && [[ "$1" == "-p" ]]; then
  DATABASE_ANONYMIZED_PWD=$2
  shift 2
fi

# GET APP_NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
fi

if [[ ! -z "$DATABASE_ANONYMIZED_PWD" ]]; then
  password="$DATABASE_ANONYMIZED_PWD"
else
  echo "You must set the DATABASE_ANONYMIZED_PWD env variable in order to run the script."
  exit 1
fi

if [[ -z "$TUNNEL_PORT" ]]; then
  echo "You must provide the TUNNEL_PORT variable."
  exit 1
fi

PRG="$BASH_SOURCE"

while [ -h "$PRG" ] ; do
	ls=$(ls -ld "$PRG")
	link=$(expr "$ls" : '.*-> \(.*\)$')
	if expr "$link" : '/.*' > /dev/null; then
		PRG="$link"
	else
		PRG=$(dirname "$PRG")"/$link"
	fi
done

ROOT_PATH=$(realpath "$(dirname "$PRG")")

cat "$ROOT_PATH"/anonymize.sql | sed -e "s/##PASSWORD##/$password/" > /tmp/anonymize_tmp.sql

if [[ -z "$APP_NAME" ]]; then
  echo "Connect to local database"
  cat /tmp/anonymize_tmp.sql | docker exec -i `docker ps | grep postgres | cut -d" " -f 1` psql -d pass_culture -U pass_culture
else
  echo "Connect to env database"
  PGPASSWORD="$TARGET_PASSWORD" psql --host 127.0.0.1 \
                               --port "$TUNNEL_PORT" \
                               --username "$TARGET_USER" \
                               --dbname "$TARGET_USER" \
                               -a  || exit 1
fi

rm /tmp/anonymize_tmp.sql

exit 0
