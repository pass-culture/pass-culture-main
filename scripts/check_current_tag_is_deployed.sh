#!/usr/bin/env bash

APP_URL="$1"
if [[ "$APP_URL" == *"backend"* ]];then
    deployed_version=$(curl -s "$APP_URL/health")
else
    deployed_version=v$(curl -s "$APP_URL/version.txt")
fi

version_to_deploy=$(git describe --contains)

echo $version_to_deploy
echo $deployed_version

[ "$deployed_version" == "$version_to_deploy" ] && exit_code=0 deploy_status="SUCCEEDED"|| exit_code=1 deploy_status="FAILED"

BOT_MESSAGE="*TEST* : Job *"$CIRCLE_JOB"* version *"$version_to_deploy"* to *"$CIRCLE_BRANCH"* seems to have *"$deploy_status"*"

curl -d text="$BOT_MESSAGE" "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$TELEGRAM_CHAT_ID&parse_mode=Markdown"

exit $exit_code