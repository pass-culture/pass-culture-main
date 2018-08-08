#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -d s3 -p s4 -o] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file (required)
    -d  SCALINGO_POSTGRESQL_URL (required)
    -p  PG_PASSWORD (required)
    -u  PG_USER (required)
    -o  get last dump from production (OVH)"
    # TODO: remove this last option when migration to Scalingo is over
    exit 0
fi

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

# PROVIDE BACKUP FILE
if [[ $# -gt 2 ]] && [[ "$1" == "-b" ]]; then
  BACKUP_FILE=$2
  shift 2
elif [[ "$*" == *"-o"* ]]; then
  SERVER_URL="deploy@api.passculture-staging.beta.gouv.fr"
  DUMP_DIRECTORY="~/dumps_prod/"
  BACKUP_FILE=$(ssh "$SERVER_URL" "ls -t $DUMP_DIRECTORY | head -n1")
  scp "$SERVER_URL":"$DUMP_DIRECTORY""$BACKUP_FILE" .
else
  echo "You must provide a existing backup file to restore."
  exit 1
fi

# GET SCALINGO_POSTGRESQL_URL
if [[ $# -gt 2 ]] && [[ "$1" == "-d" ]]; then
  POSTGRESQL_URL=$2
  shift 2
else
  echo "You must provide the SCALINGO_POSTGRESQL_URL you want to access."
  exit 1
fi

# GET SCALINGO_PG_PASSWORD
if [[ $# -gt 2 ]] && [[ "$1" == "-p" ]]; then
  PG_PASSWORD=$2
  shift 2
else
  echo "You must provide the SCALINGO_PG_PASSWORD for the database."
  exit 1
fi

# GET SCALINGO_PG_USER
if [[ $# -gt 2 ]] && [[ "$1" == "-u" ]]; then
  PG_USER=$2
  shift 2
else
  echo "You must provide the SCALINGO_PG_USER for the database."
  exit 1
fi


scalingo -a "$APP_NAME" db-tunnel "$POSTGRESQL_URL" &
sleep 3
DB_TUNNEL_PID=$!
PGPASSWORD="$PG_PASSWORD" pg_restore --clean --host 127.0.0.1 --port 10000 --username "$PG_USER" --no-owner --no-privileges --dbname "$PG_USER" "$BACKUP_FILE"
echo "$DB_TUNNEL_PID"
# for some reason kill -2 does not work (network issues maybe)
kill -9 "$DB_TUNNEL_PID"

echo "Backup restored."