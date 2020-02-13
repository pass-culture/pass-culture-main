#!/usr/bin/env bash

APP_URL="$1"
if [[ "$APP_URL" == *"backend"* ]];then
    deployed_version=$(curl -s "$APP_URL/health/api")
else
    deployed_version=v$(curl -s "$APP_URL/version.txt")
fi

version_to_deploy=$(git describe --contains)

[ "$deployed_version" == "$version_to_deploy" ] && exit 0 || exit 1
