#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-a s1 -j s2] -- program to set env var for connexion to Google API
where:
    -h  show this help text
    -a  Scalingo app name
    -j  json content"
    exit 0
fi

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a project name."
  exit 1
fi

# GET JSON (DIRTY WAY)
if [[ $# -gt 1 ]] && [[ "$1" == "-j" ]]; then
  GOOGLE_KEY=$2
  shift 2
else
  echo "You must provide the json content for Google API."
  exit 1
fi

scalingo -a "$APP_NAME" env-set PC_GOOGLE_KEY="$GOOGLE_KEY"



