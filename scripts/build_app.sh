#!/usr/bin/env bash

if [[ $# -ge 1 ]]; then
  environment="$1"
else
  echo "You need to specify an environment"
  exit 1
fi

if [ $environment == "master" ]; then
  set -a; source ./config/run_envs/"$environment" && yarn build && break
else
  set -a; source ../config/run_envs/"$environment" && yarn build && break
fi
