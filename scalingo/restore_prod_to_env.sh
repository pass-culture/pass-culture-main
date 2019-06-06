#!/usr/bin/env bash

set -o nounset
set -e

if [ -z ${1:-} ] || [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -l -z -h ] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file (required)
    -l  get last prod backup (only work on OVH server)
    -z  anonymize the backup
    -h  upgrade head"
    exit 0
fi


old_scalingo_process_pid=$(pgrep -x "scalingo" || exit 0)

if [[ "$old_scalingo_process_pid" > 1 ]]; then
    echo "A Scalingo tunnel was left opened, we are killing the old process ($old_scalingo_process_pid) before starting."
    echo "Safety first !"
    kill -9 "$old_scalingo_process_pid"
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


# OPEN TUNNEL TO DATABASE
/usr/local/bin/scalingo -a "$APP_NAME" db-tunnel postgres://"$POSTGRESQL_URL" &
sleep 3
DB_TUNNEL_PID=$!

PGPASSWORD="$PG_PASSWORD" psql --host 127.0.0.1 \
                               --port 10000 \
                               --username "$PG_USER" \
                               --dbname "$PG_DATABASE" \
                               -a -f clean_database.sql
echo "Database dropped"


PGPASSWORD="$PG_PASSWORD" pg_restore --host 127.0.0.1 \
                                         --port 10000 \
                                         --username "$PG_USER" \
                                         --no-owner \
                                         --no-privileges \
                                         --dbname "$PG_DATABASE" \
                                         "$DUMP_DIRECTORY"/"$BACKUP_FILE" 2>&1 | grep -v 'must be owner of extension' \
                                          | grep -v 'must be owner of schema public' \
                                          | grep -v ' ERROR:  schema "public" already exists' > /var/log/restore/"$APP_NAME"_error.log


if [[ $# -gt 0 ]] && [[ "$1" == "-z" ]]; then
  echo "Start anonymization"
  TARGET_USER=$PG_USER TARGET_PASSWORD=$PG_PASSWORD bash ~/pass-culture-main/anonymize_database.sh -a "$APP_NAME"
  echo "Anonymization success."
  shift 1
fi

kill -9 "$DB_TUNNEL_PID"

if grep -q 'ERROR' /var/log/restore/"$APP_NAME"_error.log; then
  echo "Restore fail.."
  echo "ERRORS found during restore backup. Please see file: /var/log/restore/"$APP_NAME"_error.log"

  curl -d text="Database Restore to $APP_NAME failed !" "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$TELEGRAM_CHAT_ID&parse_mode=Markdown"
  exit 1
elif [[ $# -gt 0 ]] && [[ "$1" == "-h" ]]; then
  echo "Upgrading Alembic Head..."
  /usr/local/bin/scalingo -a "$APP_NAME" run 'alembic upgrade head'
else
  echo "Database restored."
fi
