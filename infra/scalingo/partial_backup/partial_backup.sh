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
source /usr/local/bin/open_tunnel.sh

script_start_time=$(date +%s)
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial backup DB"

get_tunnel_database_url $app_name

echo $tunnel_database_url

echo "- Backup pre-data:"
time pg_dump --no-privileges --no-owner $tunnel_database_url --section=pre-data > "$BACKUP_PATH"/pre_data.sql

echo "- Backup post-data:"
time pg_dump $tunnel_database_url --no-privileges --no-owner --section=post-data > "$BACKUP_PATH"/post_data.sql

echo "- Backup raw data:"
recommendation_seq_id=$(psql -qtAX $tunnel_database_url -c 'select last_value from public.recommendation_id_seq;')
activity_seq_id=$(psql -qtAX $tunnel_database_url -c 'select last_value from public.activity_id_seq;')
time pg_dump $tunnel_database_url --exclude-table=recommendation --exclude-table=activity -a -F c  > "$BACKUP_PATH"/data.pgdump

echo "- Backup selected activity rows:"
time psql -Atx $tunnel_database_url -c "COPY (select * from activity where activity.id < $activity_seq_id \
  and (table_name in ('booking', 'user') and verb='update') or (table_name='stock' and verb='insert')) TO stdout;" > /tmp/activity.csv

echo "- Backup recommendation linked to booking:"
time psql -Atx $tunnel_database_url -c "COPY (select * from recommendation where recommendation.id < $recommendation_seq_id \
  AND recommendation.id in (select booking.\"recommendationId\" from booking where booking.\"recommendationId\" is not null)) \
  TO stdout;" > /tmp/reco.csv

mv /tmp/reco.csv $BACKUP_PATH/reco.csv
mv /tmp/activity.csv $BACKUP_PATH/activity.csv

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script, script duration $script_duration seconds"
