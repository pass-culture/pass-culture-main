#!/usr/bin/env bash

APP_URL="$1"
if [[ "$APP_URL" == *"backend"* ]];then
    deployed_version=$(curl -s "$APP_URL/health")
    deployed_version=45.0.0
else
    deployed_version=v$(curl -s "$APP_URL/version.txt")
    deployed_version=45.0.1
fi
#version_to_deploy=$(git describe --contains)
version_to_deploy=45.0.0

echo $version_to_deploy
echo $deployed_version

[ "$deployed_version" == "$version_to_deploy" ] && exit 0 || exit 1