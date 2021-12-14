#!/usr/bin/env bash

APP_URL="$1"
if [[ "$APP_URL" == *"backend"* ]];then
    deployed_version=$(curl -Ls "$APP_URL/health/api")
else
    deployed_version=v$(curl -Ls "$APP_URL/version.txt")
fi

# Sed here is used to remove the trailing annotation from the version
# e.g going from v165.0.0^0 to v165.0.0
version_to_deploy=$(git describe --contains | sed 's/..$//')
echo "Version to deploy: $version_to_deploy"
echo "Deployed version: $deployed_version"

[ "$deployed_version" == "$version_to_deploy" ] && exit 0 || exit 1
