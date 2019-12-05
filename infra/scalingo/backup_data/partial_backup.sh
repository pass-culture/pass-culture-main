BACKUP_PATH=$(pwd)/backup_data

mkdir $BACKUP_PATH

get_tunnel_database_port() {
  DB_TUNNEL_PID="$(pgrep -f $PG_DATABASE |tail -1)"
  DB_TUNNEL_HAS_TO_BE_TERMINATED=false

  if [ -z "$DB_TUNNEL_PID" ]
  then
    echo "Opening new tunnel to database"
    /usr/local/bin/scalingo --region osc-fr1 -a "$APP_NAME" db-tunnel postgres://"$POSTGRESQL_URL" &
    sleep 3
    DB_TUNNEL_PID=$!
    DB_TUNNEL_HAS_TO_BE_TERMINATED=true
  fi

  TUNNEL_PORT="$(lsof -Pan -p "$DB_TUNNEL_PID" -iTCP -sTCP:LISTEN -Fn |grep n |sed 's/n127.0.0.1://g')"
}

get_tunnel_database_url () {
  APP_NAME=$1

  POSTGRESQL_URL="$(/usr/local/bin/scalingo --region osc-fr1 -a $APP_NAME env |grep SCALINGO_POSTGRESQL_URL= | sed -e s,SCALINGO_POSTGRESQL_URL=postgres://,,g)"
  PG_USER="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f1)"
  PG_PASSWORD="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f2)"
  PG_DATABASE="$(echo $POSTGRESQL_URL | grep @ | cut -d'/' -f2 | cut -d '?' -f1)"

  tunnel_database_url="postgres://$PG_USER:$PG_PASSWORD@127.0.0.1:10000/$PG_DATABASE?sslmode=prefer"
}

echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : Start partial restore DB script"

get_tunnel_database_url "pass-culture-api-perf"
get_tunnel_database_port "pass-culture-api-perf"

echo TUNNEL_PORT = $TUNNEL_PORT

echo "- Backup pre-data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url -o --section=pre-data > "$BACKUP_PATH"/pre-data.sql
echo "- Backup post-data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url -o --section=post-data > "$BACKUP_PATH"/post-data.sql
#pg_dump -d pass_culture -U pass_culture -a -F c > "$BACKUP_PATH"/`date +%Y%m%d_%H%M%S`.pgdump
echo "- Backup raw data :"
time /usr/lib/postgresql/11/bin/pg_dump $tunnel_database_url --exclude-table=recommendation -a -F c  > "$BACKUP_PATH"/data.pgdump
echo "- Backup recommendation linked to booking"
time psql -Atx $tunnel_database_url -c " COPY (select * from recommendation where id in (select booking.\"recommendationId\" from booking where booking.\"recommendationId\" is not null)) TO stdout;" > /tmp/reco_perf
echo "- Backup recommendation linked to activity"
time psql -Atx $tunnel_database_url -c " COPY (select * from activity where (table_name='booking' and verb='update') or (table_name='stock' and verb='insert') or (table_name='user' and verb='update');" > /tmp/activity_perf
#mv /tmp/recommendation.csv $BACKUP_PATH/recommendation.csv

if [ "$DB_TUNNEL_HAS_TO_BE_TERMINATED" = true ]; then
  echo terminating tunnel
  kill -9 "$DB_TUNNEL_PID"
fi

script_duration=$((`date +%s`-$script_start_time))
echo "$(date -u +"%Y-%m-%dT%H:%M:%S") : End of script"