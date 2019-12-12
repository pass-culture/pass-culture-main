#!/bin/bash
set -e

BACKUP_PATH=/data/partial_backup

script_start_time=$(date +%s)

echo "- Restore pre-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/pre_data.sql || failure_alert "Restore pre-data"
echo "- Restore recommendations :"
time psql $tunnel_database_url -c "\copy recommendation FROM '$BACKUP_PATH/reco.csv';"  || failure_alert "Restore recommendation table"
echo "- Restore activity :"
time psql $tunnel_database_url -c "\copy activity FROM '$BACKUP_PATH/activity.csv';"  || failure_alert "Restore activity table"
echo "- Restore data :"
time pg_restore -d $tunnel_database_url --no-owner -j 8 --no-privileges $BACKUP_PATH/data.pgdump  || failure_alert "Restore raw data"
echo "- Restore post-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/post_data.sql || failure_alert "Restore post data"

script_duration=$((`date +%s`-$script_start_time))
echo "Restore script duration: $script_duration seconds"

return 0
