#!/usr/bin/env bash

counter=0

while [ "$counter" -lt 30 ]; do
  rm ./public/static/fontello/.fontello.session
  set -a; source node_modules/pass-culture-shared/config/run_envs/testing && yarn build && break
  echo "Waiting for Fontello to be nice with us :("
  counter=$[$counter+1]
  sleep 2
done

if [ counter -le 30 ];then
  echo "Fontello working !"
else
  echo "Too many error with Fontello download."
  exit 1
fi

