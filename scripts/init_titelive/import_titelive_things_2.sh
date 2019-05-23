#!/usr/bin/env bash

# GET APP NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-a" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide an application name."
  exit 1
fi

# GET FILE URL
if [[ $# -gt 1 ]] && [[ "$1" == "-f" ]]; then
  FILE_LINK=$2
  shift 2
else
  echo "You must provide a file URL."
  exit 1
fi

scalingo -a "$APP_NAME" run -d --size 2XL "wget -O Titelive.zip $FILE_LINK
&& unzip Titelive.zip
&& python scripts/pc.py import_titelive_full_table -f Differentiel-20190115.tit"

