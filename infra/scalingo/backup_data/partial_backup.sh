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

mkdir -p $BACKUP_PATH
source open_tunnel.sh

script_start_time=$(date +%s)
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB"

get_tunnel_database_port $APP_NAME
get_tunnel_database_url $APP_NAME

echo "- Backup pre-data :"
time /usr/lib/postgresql/11/bin/pg_dump --no-privileges --no-owner $tunnel_database_url --section=pre-data > "$BACKUP_PATH"/pre_data_$APP_NAME.sql
exit 0
echo "- Backup post-data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url --no-privileges --no-owner --section=post-data > "$BACKUP_PATH"/post_data_$APP_NAME.sql
echo "- Backup raw data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url --exclude-table=recommendation --exclude-table=activity -a -F c  > "$BACKUP_PATH"/data_$APP_NAME.pgdump
echo "- Backup recommendation linked to booking"
time psql -Atx $tunnel_database_url -c "COPY (select * from recommendation where id in (select booking.\"recommendationId\" from booking where booking.\"recommendationId\" is not null)) TO stdout;" > /tmp/reco_$APP_NAME
echo "- Backup selected activity rows"
time psql -Atx $tunnel_database_url -c "COPY (select * from activity where (table_name='booking' and verb='update') or (table_name='stock' and verb='insert') or (table_name='user' and verb='update')) TO stdout;" > /tmp/activity_$APP_NAME

#mv /tmp/recommendation.csv $BACKUP_PATH/recommendation.csv
mv /tmp/reco_$APP_NAME $BACKUP_PATH/reco_$APP_NAME
mv /tmp/activity_$APP_NAME $BACKUP_PATH/activity_$APP_NAME

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script, script duration $script_duration seconds"