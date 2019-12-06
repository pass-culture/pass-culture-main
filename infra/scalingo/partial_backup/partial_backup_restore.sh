#!/bin/bash
set -e

BACKUP_PATH=/data/partial_backup

script_start_time=$(date +%s)

echo "*** Restore pre-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/pre_data.sql
echo "*** Restore recommendations :"
time psql $tunnel_database_url -c "\copy recommendation FROM '$BACKUP_PATH/reco';"
echo "*** Restore activity :"
time psql $tunnel_database_url -c "\copy activity FROM '$BACKUP_PATH/activity';"
echo "*** Restore data :"
time pg_restore -d $tunnel_database_url --no-owner -j 8 --no-privileges $BACKUP_PATH/data.pgdump
echo "*** Restore post-data :"
time psql $tunnel_database_url -f $BACKUP_PATH/post_data.sql

script_duration=$((`date +%s`-$script_start_time))
echo "Restore script duration: $script_duration seconds"

return 0