#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-n s1] -- program to set env var for connexion between
    OVH Bucket and Scalingo
where:
    -h  show this help text
    -a  Scalingo app name
    -u  OVH openstack username
    -p  OVH openstack password
    -c  OVH bucket name"
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

# GET OPENSTACK USERNAME
if [[ $# -gt 1 ]] && [[ "$1" == "-u" ]]; then
  OVH_USER=$2
  shift 2
else
  echo "You must provide a openstack user."
  exit 1
fi

# GET OPENSTACK PASSWORD
if [[ $# -gt 1 ]] && [[ "$1" == "-p" ]]; then
  OVH_PASSWORD=$2
  shift 2
else
  echo "You must provide the openstack user password."
  exit 1
fi

# GET OPENSTACK BUCKET NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-c" ]]; then
  OVH_BUCKET_NAME=$2
  shift 2
else
  echo "You must provide a bucket name."
  exit 1
fi

# SET ENV VAR FOR CONNECTION
scalingo -a "$APP_NAME" env-set OVH_USER="$OVH_USER"
scalingo -a "$APP_NAME" env-set OVH_PASSWORD="$OVH_PASSWORD"
scalingo -a "$APP_NAME" env-set OVH_BUCKET_NAME="$OVH_BUCKET_NAME"



