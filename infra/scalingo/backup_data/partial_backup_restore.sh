#!/bin/bash
set -e

BACKUP_PATH=/data
TIMEFORMAT=%R

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

source open_tunnel.sh

script_start_time=$(date +%s)
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB script"

get_tunnel_database_port $APP_NAME
get_tunnel_database_url $APP_NAME

echo TUNNEL_PORT = $TUNNEL_PORT
echo $tunnel_database_url

psql $tunnel_database_url -f /tmp/clean_database.sql
echo "*** Database cleaned"

#exit 0

echo "*** Restore pre-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/staging/pre_data.sql
echo "*** Restore recommendations :"
time psql $tunnel_database_url -c "\copy recommendation FROM '$BACKUP_PATH/staging/reco';"
echo "*** Restore activity :"
time psql $tunnel_database_url -c "\copy activity FROM '$BACKUP_PATH/staging/activity';"
echo "*** Restore data :"
time pg_restore -d $tunnel_database_url --no-owner -j 8 --no-privileges $BACKUP_PATH/staging/data.pgdump
echo "*** Restore post-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/staging/post_data.sql


if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script, script duration $script_duration seconds"
exit 0