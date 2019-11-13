#!/usr/bin/env bash

set -o nounset
set -e

script_start_time=`date +%s`

if [ -z ${1:-} ] || [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -l -z -h ] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file (required if -l is not provided)
    -l  get last prod backup (only works on OVH server)
    -z  anonymize the backup
    -h  upgrade head"
    exit 0
fi

DUMP_DIRECTORY=/data/

echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start restore DB script"

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

# PROVIDE BACKUP FILE
if [[ $# -gt 1 ]] && [[ "$1" == "-b" ]]; then
  BACKUP_FILE=$2
  shift 2
elif [[ "$*" == *"-l"* ]]; then
  BACKUP_FILE=$(cd "$DUMP_DIRECTORY" && find -L . ! -size 0 -type f -printf "%T@ %p\n" | sort -n  | tail -1 | cut -d' ' -f 2)
  shift 1
else
  echo "You must provide a existing backup file to restore."
  exit 1
fi

# GET SCALINGO DATABASE URL
POSTGRESQL_URL="$(/usr/local/bin/scalingo -a $APP_NAME env |grep SCALINGO_POSTGRESQL_URL= | sed -e s,SCALINGO_POSTGRESQL_URL=postgres://,,g)"

# EXTRACT THE USER AND PASSWORD
PG_USER="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f1)"
PG_PASSWORD="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f2)"
PG_DATABASE="$(echo $POSTGRESQL_URL | grep @ | cut -d'/' -f2 | cut -d '?' -f1)"

DB_TUNNEL_PID="$(pgrep -f $PG_DATABASE |tail -1)"
DB_TUNNEL_HAS_TO_BE_TERMINATED=false

if [ -z "$DB_TUNNEL_PID" ]
then
  # OPEN TUNNEL TO DATABASE
  /usr/local/bin/scalingo -a "$APP_NAME" db-tunnel postgres://"$POSTGRESQL_URL" &
  sleep 3
  DB_TUNNEL_PID=$!
  DB_TUNNEL_HAS_TO_BE_TERMINATED=true
fi

TUNNEL_PORT="$(lsof -Pan -p "$DB_TUNNEL_PID" -iTCP -sTCP:LISTEN -Fn |grep n |sed 's/n127.0.0.1://g')"
echo TUNNEL_PORT = $TUNNEL_PORT


PGPASSWORD="$PG_PASSWORD" psql --host 127.0.0.1 \
                               --port "$TUNNEL_PORT" \
                               --username "$PG_USER" \
                               --dbname "$PG_DATABASE" \
                               -a -f /usr/local/bin/clean_database.sql

echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Database dropped"


PGPASSWORD="$PG_PASSWORD" pg_restore --host 127.0.0.1 \
                                         --port "$TUNNEL_PORT" \
                                         --username "$PG_USER" \
                                         --no-owner \
                                         -j 2 \
                                         --no-privileges \
                                         --dbname "$PG_DATABASE" \
                                         "$DUMP_DIRECTORY"/"$BACKUP_FILE" 2>&1 | grep -v 'must be owner of extension' \
                                          | grep -v 'must be owner of schema public' \
                                          | grep -v ' ERROR:  schema "public" already exists' > /var/log/restore/"$APP_NAME"_error.log


if [[ $# -gt 0 ]] && [[ "$1" == "-z" ]]; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start anonymization"
  TUNNEL_PORT=$TUNNEL_PORT TARGET_USER=$PG_USER TARGET_PASSWORD=$PG_PASSWORD bash /usr/local/bin/anonymize_database.sh -a "$APP_NAME"
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Anonymization success."
  shift 1
fi

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

if grep -q 'ERROR' /var/log/restore/"$APP_NAME"_error.log; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Restore fail."
  echo "Script duration : $((script_end_time-script_start_time))"
  echo "ERRORS found during restore backup. Please see file: /var/log/restore/"$APP_NAME"_error.log"

  curl -d text="Database Restore to $APP_NAME failed !" "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$TELEGRAM_CHAT_ID&parse_mode=Markdown"
  exit 1
elif [[ $# -gt 0 ]] && [[ "$1" == "-h" ]]; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Upgrading Alembic Head."
  /usr/local/bin/scalingo -a "$APP_NAME" run 'alembic upgrade head'
else
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") Database restored."
fi

script_end_time=`date +%s`
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script"
echo "Script duration : $((script_end_time-script_start_time))"
