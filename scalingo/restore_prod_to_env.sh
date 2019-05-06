#!/usr/bin/env bash

set -o nounset

if [ -z ${1:-} ] || [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -l] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file (required)
    -l  get last prod backup (only work on OVH server)"
    exit 0
fi

old_scalingo_process_pid=$(pgrep -x "scalingo")
if [[ "$old_scalingo_process_pid" > 1 ]]; then
    echo "A Scalingo tunnel was left opened, we are killing the old process ($old_scalingo_process_pid) before starting."
    echo "Safety first !"
    sudo kill -9 "$old_scalingo_process_pid"
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
if [[ $# -gt 1 ]] && [[ "$1" == "-b" ]]; then
  DUMP_DIRECTORY=~/pass-culture-main/db_prod_dumps
  BACKUP_FILE=$2
  shift 2
elif [[ "$*" == *"-l"* ]]; then
  DUMP_DIRECTORY=~/pass-culture-main/db_prod_dumps
  BACKUP_FILE=$(cd "$DUMP_DIRECTORY" && find -L . ! -size 0 -type f -printf "%T@ %p\n" | sort -n  | tail -1 | cut -d' ' -f 2)
else
  echo "You must provide a existing backup file to restore."
  exit 1
fi

# GET SCALINGO DATABASE URL
POSTGRESQL_URL_OLD="$(/usr/local/bin/scalingo -a $APP_NAME env |grep SCALINGO_POSTGRESQL_URL= | sed -e s,SCALINGO_POSTGRESQL_URL=postgres://,,g)"

# EXTRACT THE USER FROM URL
PG_USER_OLD="$(echo $POSTGRESQL_URL_OLD | grep @ | cut -d@ -f1 | cut -d':' -f1)"

# DELETE APPLICATION ADDON
echo $PG_USER_OLD | /usr/local/bin/scalingo -a $APP_NAME addons-remove $PG_USER_OLD

# RE-ATTACHING APPLICATION ADDON
/usr/local/bin/scalingo -a $APP_NAME addons-add postgresql 4g

# GET NEW SCALINGO DATABASE URL
NEXT_WAIT_TIME=0
POSTGRESQL_URL=$POSTGRESQL_URL_OLD

until [ "$POSTGRESQL_URL" != "$POSTGRESQL_URL_OLD" ] || [ $NEXT_WAIT_TIME -eq 60 ]; do
   POSTGRESQL_URL="$(/usr/local/bin/scalingo -a $APP_NAME env |grep SCALINGO_POSTGRESQL_URL= | sed -e s,SCALINGO_POSTGRESQL_URL=postgres://,,g)"
   sleep 2
   let NEXT_WAIT_TIME++
done
sleep 10

# EXTRACT THE USER AND PASSWORD
PG_USER="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f1)"
PG_PASSWORD="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f2)"


# OPEN TUNNEL TO DATABASE
/usr/local/bin/scalingo -a "$APP_NAME" db-tunnel postgres://"$POSTGRESQL_URL" &
sleep 10
DB_TUNNEL_PID=$!

echo "Tunnel to database open"

PGPASSWORD="$PG_PASSWORD" pg_restore --host 127.0.0.1 \
                                         --port 10000 \
                                         --username "$PG_USER" \
                                         --no-owner \
                                         --no-privileges \
                                         --dbname "$PG_USER" \
                                         "$DUMP_DIRECTORY"/"$BACKUP_FILE" 2>&1 | grep -v 'must be owner of extension' \
                                          | grep -v 'must be owner of schema public' \
                                          | grep -v ' ERROR:  schema "public" already exists' > restore_"$APP_NAME"_error.log

echo "Backup restored."
sudo kill -9 "$DB_TUNNEL_PID"

if grep -q 'ERROR' restore_"$APP_NAME"_error.log; then
  echo "Restore fail.."
  echo "ERRORS found during restore backup. Please see file: restore_"$APP_NAME"_error.log"
else
  echo "Restarting backend.."
  /usr/local/bin/scalingo -a "$APP_NAME" run 'alembic upgrade head'
  echo "Application restarted and ready to use."
fi
