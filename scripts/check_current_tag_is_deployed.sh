#!/usr/bin/env bash

APP_URL="$1"
api_version=v$(curl -s "$APP_URL/version.txt")
version_to_deploy=$(git tag -l --points-at HEAD)
if [ "$api_version" != "$version_to_deploy" ];then
  echo "Deploy seems to have fail"
  exit 1
fi
echo "Deploy confirmed !"
