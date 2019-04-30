#!/usr/bin/env bash

APP_URL="$1"
if [[ "$APP_URL" == *"backend"* ]];then
    deployed_version=$(curl -s "$APP_URL/health")
else
    deployed_version=v$(curl -s "$APP_URL/version.txt")
fi

if [[ ! "$deployed_version" =~ "$version_to_deploy" ]];then
  echo "Deploy seems to have fail"
  exit 1
fi
echo "Deploy confirmed !"