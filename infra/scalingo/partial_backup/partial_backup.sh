#!/bin/bash
set -e

BACKUP_PATH=/data/partial_backup
TIMEFORMAT=%R

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  app_name=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

mkdir -p $BACKUP_PATH
source open_tunnel.sh

script_start_time=$(date +%s)
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB"

get_tunnel_database_port $app_name
get_tunnel_database_url $app_name

echo "- Backup pre-data :"
time /usr/lib/postgresql/11/bin/pg_dump --no-privileges --no-owner $tunnel_database_url --section=pre-data > "$BACKUP_PATH"/pre_data_$app_name.sql
exit 0
echo "- Backup post-data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url --no-privileges --no-owner --section=post-data > "$BACKUP_PATH"/post_data_$app_name.sql
echo "- Backup raw data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url --exclude-table=recommendation --exclude-table=activity -a -F c  > "$BACKUP_PATH"/data_$app_name.pgdump
echo "- Backup recommendation linked to booking"
time psql -Atx $tunnel_database_url -c "COPY (select * from recommendation where id in (select booking.\"recommendationId\" from booking where booking.\"recommendationId\" is not null)) TO stdout;" > /tmp/reco_$app_name
echo "- Backup selected activity rows"
time psql -Atx $tunnel_database_url -c "COPY (select * from activity where (table_name='booking' and verb='update') or (table_name='stock' and verb='insert') or (table_name='user' and verb='update')) TO stdout;" > /tmp/activity_$app_name

#mv /tmp/recommendation.csv $BACKUP_PATH/recommendation.csv
mv /tmp/reco_$app_name $BACKUP_PATH/reco_$app_name
mv /tmp/activity_$app_name $BACKUP_PATH/activity_$app_name

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script, script duration $script_duration seconds"