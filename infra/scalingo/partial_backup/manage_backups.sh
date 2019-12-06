#!/bin/bash

show_help() {
cat << EOF
Usage: ${0##*/} [-hcuz] [-a APP NAME]
Restore database backup with the last backup in \$BACKUP_PATH
    -h            display this help and exit
    -a APP_NAME   The application that will have its database restored
    -c            Create test users at the end of the restore process
    -d            Drop database only
    -n            No backup restoration (default to false)
    -r            Region where the app is hosted, default is osc-fr1
    -u            Upgrade head
    -z            Run the anonymization script
EOF
}

upgrade_head=false
anonymize=false
create_users=false
drop_database=false
restore_backup=true
SCALINGO_REGION=osc-fr1
TIMEFORMAT=%R

OPTIND=1

while getopts hcdnuza:r: opt; do
    case $opt in
        h)
            show_help
            exit 0
            ;;
        a)  app_name=$OPTARG
            ;;
        c)  create_users=true
            ;;
        d)  drop_database=true
            ;;
        r)  SCALINGO_REGION=$OPTARG
            ;;
        n)  restore_backup=false
            ;;
        u)  upgrade_head=true
            ;;
        z)  anonymize=true
            ;;
        *)
            show_help >&2
            exit 1
            ;;
    esac
done
shift "$((OPTIND-1))"

if [ ! $app_name ]
then
  echo "ERROR: You have to provide an application name : '-a app_name'"
  show_help
  exit 1
fi

source open_tunnel.sh
get_tunnel_database_url $app_name

if [ -z "$TUNNEL_PORT" ]; then
  echo "Could not connect to database."
  exit 1
fi

echo "Local postgres url : $tunnel_database_url $TUNNEL_PORT"


if "$drop_database" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start database drop"
  time psql $tunnel_database_url -a -f /usr/local/bin/clean_database.sql \
    && echo "Database dropped" || echo "Database drop Failed"
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of database drop"
fi

if "$restore_backup" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB script"
  source partial_backup_restore.sh && echo "Partial restore completed" || echo "Partial restore Failed"
fi

if "$anonymize" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start anonymization"
  TUNNEL_PORT=$TUNNEL_PORT TARGET_USER=$PG_USER TARGET_PASSWORD=$PG_PASSWORD bash anonymize_database.sh -a "$app_name" \
    && echo "Anonymized" || echo "Anonymization Failed"
fi

if "$upgrade_head" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Upgrading Alembic Head."
  time /usr/local/bin/scalingo --region $SCALINGO_REGION -a "$app_name" run 'alembic upgrade head' \
    && echo "Alembic head upgraded" || echo "Alembic head upgrad Failed"
fi

if "$create_users" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start user importation"
  echo create_users $create_users
  time /usr/local/bin/scalingo --region $SCALINGO_REGION -a "$app_name" run  /var/lib/scalingo/data_$app_name.csv \
    -f /var/lib/scalingo/import_users.py python /tmp/uploads/import_users.py data_$app_name.csv \
     && echo "User imported" || echo "User importation Failed"
fi

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of backup operation"
exit 0