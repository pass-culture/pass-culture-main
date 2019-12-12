#!/bin/bash

get_tunnel_database_url() {
  app_name=$1

  POSTGRESQL_URL="$(/usr/local/bin/scalingo --region $SCALINGO_REGION -a $app_name env |grep SCALINGO_POSTGRESQL_URL= | sed -e s,SCALINGO_POSTGRESQL_URL=postgres://,,g)"
  echo $POSTGRESQL_URL
  if [ -z "$POSTGRESQL_URL" ]; then
    return
  fi

  PG_DATABASE="$(echo $POSTGRESQL_URL | grep @ | cut -d'/' -f2 | cut -d '?' -f1)"
  PG_USER="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f1)"
  PG_PASSWORD="$(echo $POSTGRESQL_URL | grep @ | cut -d@ -f1 | cut -d':' -f2)"

  echo $PG_DATABASE
  DB_TUNNEL_PID="$(pgrep -f $PG_DATABASE | tail -1)"
  DB_TUNNEL_HAS_TO_BE_TERMINATED=false

  if [ -z "$DB_TUNNEL_PID" ]
  then
    echo "Opening new tunnel to database"
    /usr/local/bin/scalingo --region $SCALINGO_REGION -a "$app_name" db-tunnel postgres://"$POSTGRESQL_URL" &
    sleep 3
    DB_TUNNEL_PID=$!
    DB_TUNNEL_HAS_TO_BE_TERMINATED=true
  fi

  echo $DB_TUNNEL_PID
  TUNNEL_PORT="$(lsof -Pan -w -p "$DB_TUNNEL_PID" -iTCP -sTCP:LISTEN -Fn | grep n | sed 's/n127.0.0.1://g')"
  tunnel_database_url="postgres://$PG_USER:$PG_PASSWORD@127.0.0.1:$TUNNEL_PORT/$PG_DATABASE?sslmode=prefer"
}
