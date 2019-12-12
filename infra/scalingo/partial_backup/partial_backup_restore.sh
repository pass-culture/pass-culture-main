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
backup_file_timestamp=$(stat $BACKUP_PATH/data.pgdump -c %y)
echo "Restore script duration: $script_duration seconds"

psql $tunnel_database_url -c "CREATE TABLE db_restore_infos (backup_file_timestamp TIMESTAMP NOT NULL, end_of_db_restore TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, restore_duration INT NOT NULL);"
psql $tunnel_database_url -c "INSERT INTO db_restore_infos (backup_file_timestamp, restore_duration) values ('$backup_file_timestamp', '$script_duration');"

return 0
