#!/bin/bash

CURRENT_ROOT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
CURRENT_DATA=$(df /data | grep /data | awk '{ print $5}' | sed 's/%//g')
THRESHOLD=90

if [ "$CURRENT_ROOT" -gt "$THRESHOLD" ] ; then
  curl -X POST -H 'Content-type: application/json' --data "{'text': 'Disk free space is running low on bastion's ROOT partition'}" $SLACK_OPS_BOT_URL
fi

if [ "$CURRENT_DATA" -gt "$THRESHOLD" ] ; then
  curl -X POST -H 'Content-type: application/json' --data "{'text': 'Disk free space is running low on bastion's DATA partition'}" $SLACK_OPS_BOT_URL
fi
