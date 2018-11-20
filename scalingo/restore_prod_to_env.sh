#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -b s2 -l] -- program to restore a backup file on Scalingo database
where:
    -h  show this help text
    -a  Scalingo app name (required)
    -b  path to backup file (required)
    -l  get last prod backup (only work on OVH server)"
    exit 0
fi

if pgrep -x "scalingo" > /dev/null
then
    echo "A Scalingo tunnel was left opened, restore backup will not start."
    echo "Safety first !"
    exit 1
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
  DUMP_DIRECTORY=.
  BACKUP_FILE=$2
  shift 2
elif [[ "$*" == *"-l"* ]]; then
  DUMP_DIRECTORY=~/pass-culture-main/db_prod_dumps
  BACKUP_FILE=$(cd "$DUMP_DIRECTORY" && find -L . ! -size 0 -type f -printf "%T@ %p\n" | sort -n  | tail -1 | cut -d' ' -f 2)
else
  echo "You must provide a existing backup file to restore."
  exit 1
fi

# GET SCALINGO INFORMATION FOR TESTING ENV
if [[ "$APP_NAME" == "pass-culture-api-dev" ]] \
    &&  [[ ! -z "$SCALINGO_POSTGRESQL_URL_TESTING" ]] \
    &&  [[ ! -z "$SCALINGO_USER_TESTING" ]] \
    &&  [[ ! -z "$SCALINGO_PWD_TESTING" ]]; then
  POSTGRESQL_URL="$SCALINGO_POSTGRESQL_URL_TESTING"
  PG_PASSWORD="$SCALINGO_PWD_TESTING"
  PG_USER="$SCALINGO_USER_TESTING"
  shift 2
# GET SCALINGO INFORMATION FRO STAGING ENV
elif [[ "$APP_NAME" == "pass-culture-api-staging" ]] \
    &&  [[ ! -z "$SCALINGO_POSTGRESQL_URL_STAGING" ]] \
    &&  [[ ! -z "$SCALINGO_USER_STAGING" ]] \
    &&  [[ ! -z "$SCALINGO_PWD_STAGING" ]]; then
  POSTGRESQL_URL="$SCALINGO_POSTGRESQL_URL_STAGING"
  PG_PASSWORD="$SCALINGO_PWD_STAGING"
  PG_USER="$SCALINGO_USER_STAGING"
  shift 2
else
  echo "You must set the required env variables for the requested env."
  exit 1
fi

/usr/local/bin/scalingo -a "$APP_NAME" db-tunnel "$POSTGRESQL_URL" &
sleep 3
DB_TUNNEL_PID=$!

PGPASSWORD="$PG_PASSWORD" pg_restore --clean \
                                         --host 127.0.0.1 \
                                         --port 10000 \
                                         --username "$PG_USER" \
                                         --no-owner \
                                         --no-privileges \
                                         --dbname "$PG_USER" \
                                         "$DUMP_DIRECTORY"/"$BACKUP_FILE" 2>&1 | grep -v 'must be owner of extension plpgsql' \
                                          | grep -v 'must be owner of schema public' \
                                          | grep -v 'ERROR:  schema "public" already exists' > restore_"$ENV"_error.log

sudo kill -9 "$DB_TUNNEL_PID"
echo "Backup restored."

if grep -q 'ERROR' restore_"$ENV"_error.log; then
  echo "Backup fail.."
  echo "ERRORS found during restore backup. Please see file: restore_dev_error.log"
else
  echo "Backup success !"
  echo "Restarting backend.."
  /usr/local/bin/scalingo -a "$APP_NAME" restart
  echo "Application restarted and ready to use."
fi
