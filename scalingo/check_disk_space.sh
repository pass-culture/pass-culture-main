#!/bin/bash

CURRENT_ROOT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
CURRENT_DATA=$(df /data | grep /data | awk '{ print $5}' | sed 's/%//g')
THRESHOLD=90

if [ "$CURRENT_ROOT" -gt "$THRESHOLD" ] ; then
  curl -d text="Disk free space is critically low on bastion's ROOT partition" "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$TELEGRAM_CHAT_ID&parse_mode=Markdown"
fi

if [ "$CURRENT_DATA" -gt "$THRESHOLD" ] ; then
  curl -d text="Disk free space is critically low on bastion's DATA partition" "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$TELEGRAM_CHAT_ID&parse_mode=Markdown"
fi
