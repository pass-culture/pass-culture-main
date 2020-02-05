#!/bin/bash

failure_alert() {
  message="$app_name backup restore failed at step: $1"
  curl -X POST -H 'Content-type: application/json' --data "{'text': '$message'}" $SLACK_OPS_BOT_URL
  end_script
  exit 1
}

show_help() {
cat << EOF
Usage: ${0##*/} [-hcuz] [-a APP NAME]
Restore database backup with the last backup in \$BACKUP_PATH
    -h            Display this help and exit
    -a APP_NAME   The application that will have its database restored
    -c            Create test users at the end of the restore process
    -d            Drop database
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

script_parameters="hcdnuza:r:"
while getopts $script_parameters opt; do
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
kill_tunnel_if_exist $app_name
get_tunnel_database_url $app_name

if [ -z "$TUNNEL_PORT" ]; then
  failure_alert "Connection to Database."
fi

echo "Local postgres url : $tunnel_database_url $TUNNEL_PORT"

if "$drop_database" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start database drop"
  time psql $tunnel_database_url -a -f /usr/local/bin/clean_database.sql \
    && echo "Database dropped" || failure_alert "Database drop"
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of database drop"
fi

if "$restore_backup" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB script"
  source partial_backup_restore.sh && echo "Partial restore completed"
fi

if "$anonymize" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start anonymization"
  TUNNEL_PORT=$TUNNEL_PORT TARGET_USER=$PG_USER TARGET_PASSWORD=$PG_PASSWORD bash anonymize_database.sh -a "$app_name" \
    && echo "Anonymized" || failure_alert "Anonymization"
fi

if "$upgrade_head" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Upgrading Alembic Head."
  time /usr/local/bin/scalingo --region $SCALINGO_REGION -a "$app_name" run 'alembic upgrade head' \
    && echo "Alembic head upgraded" || failure_alert "Alembic head upgrade"
fi

if "$create_users" ; then
  echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start user importation"
  echo create_users $create_users
  time /usr/local/bin/scalingo --region $SCALINGO_REGION -a "$app_name" run -f /var/lib/scalingo/data_$app_name.csv \
    -f /var/lib/scalingo/import_users.py python /tmp/uploads/import_users.py data_$app_name.csv \
     && echo "User imported" || failure_alert "User importation"
fi

kill_tunnel_if_exist $app_name

echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of backup operations"
exit 0
