#!/usr/bin/env bash

set -o nounset

if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1] -- program to clean indices on elasticsearch instance
where:
    -h  show this help text
    -a  Scalingo monitoring app name (required)"
    exit 0
fi

old_scalingo_process_pid=$(pgrep -x "scalingo")
if [ "$old_scalingo_process_pid" > 1 ]; then
then
    echo "A Scalingo tunnel was left opened, we are killing the old process ($old_scalingo_process_pid) before starting."
    echo "Safety first !"
    sudo kill -9 "$old_scalingo_process_pid"
fi

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

/usr/local/bin/scalingo -a "$APP_NAME" db-tunnel "$ELASTICSEARCH_URL" &
sleep 3
DB_TUNNEL_PID=$!

curator --config config.yml action.yml

sudo kill -9 "$DB_TUNNEL_PID"
echo "Indices cleaned."
