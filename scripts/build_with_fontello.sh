#!/usr/bin/env bash


if [[ $# -ge 1 ]];
then
    environment="$1"
else
    echo "You need to specify an environment"
    exit 1
fi

counter=0

while [ "$counter" -lt 30 ]; do
  rm ./public/static/fontello/.fontello.session
  set -a; source ./config/run_envs/"$environment" && yarn build && break
  echo "Waiting for Fontello to be nice with us :("
  counter=$[$counter+1]
  sleep 2
done

if [ $counter -le 30 ];then
  echo "Fontello working !"
else
  echo "Too many error with Fontello download."
  exit 1
fi

