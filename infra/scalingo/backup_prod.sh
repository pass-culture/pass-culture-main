#!/usr/bin/env bash

set -o nounset


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -d s3 -p s4] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file
    -d  SCALINGO_POSTGRESQL_URL (required)
    -p  PG_PASSWORD (required)
    -u  PG_USER (required)"
    exit 0
fi

echo "--------"
script_start_time=`date +%s`
echo $(date)

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

# PROVIDE BACKUP PATH
if [[ $# -gt 2 ]] && [[ "$1" == "-b" ]]; then
  BACKUP_PATH=$2
  shift 2
else
  BACKUP_PATH=/data/
  echo "Using default BACKUP_PATH. $BACKUP_PATH"
fi

# GET SCALINGO_POSTGRESQL_URL
if [[ $# -gt 2 ]] && [[ "$1" == "-d" ]]; then
  POSTGRESQL_URL=$2
  shift 2
elif [[ "$SCALINGO_POSTGRESQL_URL_PROD" =~ "postgres://" ]]; then
  POSTGRESQL_URL="$SCALINGO_POSTGRESQL_URL_PROD"
  echo postgresql url : $POSTGRESQL_URL
else
  echo "You must provide the SCALINGO_POSTGRESQL_URL you want to access."
  exit 1
fi

# GET SCALINGO_PG_PASSWORD
if [[ $# -gt 2 ]] && [[ "$1" == "-p" ]]; then
  PG_PASSWORD=$2
  shift 2
elif [[ ! -z "$SCALINGO_PWD_PROD" ]]; then
  PG_PASSWORD="$SCALINGO_PWD_PROD"
else
  echo "You must provide the SCALINGO_PG_PASSWORD for the database."
  exit 1
fi

# GET SCALINGO_PG_USER
if [[ $# -gt 1 ]] && [[ "$1" == "-u" ]]; then
  PG_USER=$2
  shift 2
elif [[ ! -z "$SCALINGO_USER_PROD" ]]; then
  PG_USER="$SCALINGO_USER_PROD"
else
  echo "You must provide the SCALINGO_PG_USER for the database."
  exit 1
fi

DB_TUNNEL_PID="$(pgrep -f $(echo $POSTGRESQL_URL | cut -d '?' -f1) |tail -1)"
DB_TUNNEL_HAS_TO_BE_TERMINATED=false

if [ -z "$DB_TUNNEL_PID" ]
then
  # OPEN TUNNEL TO DATABASE
  /usr/local/bin/scalingo -a "$APP_NAME" db-tunnel "$POSTGRESQL_URL" &
  sleep 3
  DB_TUNNEL_PID=$!
  DB_TUNNEL_HAS_TO_BE_TERMINATED=true
  TUNNEL_PORT="$(lsof -Pan -p "$DB_TUNNEL_PID" -iTCP -sTCP:LISTEN -Fn |grep n |sed 's/n127.0.0.1://g')"
  echo "Waiting for connection to be up"
  is_connection_ready=1
  while [ "$is_connection_ready" != 0 ]
  do
    pg_isready -h localhost -p $TUNNEL_PORT > /dev/null 2>&1
    is_connection_ready=$?
    sleep 1
  done
fi

TUNNEL_PORT="$(lsof -Pan -p "$DB_TUNNEL_PID" -iTCP -sTCP:LISTEN -Fn |grep n |sed 's/n127.0.0.1://g')"

echo "Connection up !"
echo "Current db-tunnel PID : $DB_TUNNEL_PID, tunnel port : $TUNNEL_PORT"

exit 1

echo "Start backup process."
mkdir -p "$BACKUP_PATH"
PGPASSWORD="$PG_PASSWORD" pg_dump --host 127.0.0.1 --port $TUNNEL_PORT --username "$PG_USER" --dbname "$PG_USER" -F c > "$BACKUP_PATH"/`date +%Y%m%d_%H%M%S`.pgdump

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script"
