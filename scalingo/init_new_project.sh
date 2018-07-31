#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

#TODO: improve script by getting parameters from template file maybe ?
#TODO: set all env var from a single file ?

if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-n s1 -r s2 -u s3 -d s4 -b i1 -j -k s4 s5] -- program to create new project on Scalingo
where:
    -h  show this help text
    -n  new Scalingo project name (required)
    -r  set the remote target for the project (default: scalingo)
    -u  set the custom domain name (optional)
    -d  set database plan size (default: free)
    -b  set number of backends to deploy (default: 1)
    -j  set the env var MAILJET_API_SECRET (required)
    -k  set the env var MAILJET_API_KEY (required)
    -e  set env variable ENV (optionnal)"
    exit 0
fi

# GET APPLICATION NAME
if [[ $# -gt 1 ]] && [[ "$1" == "-n" ]]; then
  APP_NAME=$2
  shift 2
else
  echo "You must provide a name for the new project."
  exit 1
fi

# GET REMOTE
if [[ $# -gt 1 ]] && [[ "$1" == "-r" ]]; then
  APP_REMOTE=$2
  shift 2
else
  APP_REMOTE=${APP_REMOTE:-'scalingo'}
fi

# GET CUSTOM DNS
if [[ $# -gt 1 ]] && [[ "$1" == "-u" ]]; then
  APP_CUSTOM_DNS=$2
  shift 2
fi

# GET DATABASE SIZE
if [[ $# -gt 1 ]] && [[ "$1" == "-d" ]]; then
  DATABASE_SIZE=$2
  shift 2
else
  echo "No database size provided. Use free plan."
  DATABASE_SIZE=${DATABASE_SIZE:-'free'}
fi

# GET NUMBER OF BACKENDS
if [[ $# -gt 1 ]] && [[ "$1" == "-b" ]]; then
  NB_BACKENDS=$2
  shift 2
else
  echo "Start 1 backend."
  NB_BACKENDS=${NB_BACKENDS:-'1'}
fi

# CREATE NEW PROJECT ON SCALINGO
echo "Creating new app on Scalingo..."
if [ "$APP_REMOTE" = "" ]; then
  scalingo create "$APP_NAME"
else
  scalingo create "$APP_NAME" --remote "$APP_REMOTE"
fi

# ADD DATABASE PLUGIN
echo "Add Postgresql addon to app..."
scalingo -a "$APP_NAME" addons-add postgresql "$DATABASE_SIZE"

# GET MAILJET_API_SECRET
if [[ $# -gt 1 ]] && [[ "$1" == "-j" ]]; then
  scalingo -a "$APP_NAME" env-set MAILJET_API_SECRET="$2"
  shift 2
else
  echo "You must provide a # GET MAILJET_API_SECRET."
  exit 1
fi

# GET MAILJET_API_KEY
if [[ $# -gt 1 ]] && [[ "$1" == "-k" ]]; then
  scalingo -a "$APP_NAME" env-set MAILJET_API_KEY="$2"
  shift 2
else
  echo "You must provide a MAILJET_API_KEY."
  exit 1
fi

# IF PROVIDED ADD ENV VAR
if [[ $# -gt 1 ]] && [[ "$1" == "-e" ]]; then
  scalingo -a "$APP_NAME" env-set ENV="$2"
  shift 2
else
  echo "No env var ENV provided."
fi

# DEPLOY CURRENT GIT BRANCH TO SCALINGO
readonly GIT_LOCAL_BRANCH_NAME=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
echo "Add remote in local git..."
git remote add "$APP_REMOTE" git@scalingo.com:"$APP_NAME".git
echo "Deploying current repo to new app on Scalingo..."
git push "$APP_REMOTE" "$GIT_LOCAL_BRANCH_NAME":master


# SCALE APPLICATION TO EXPECTED NUMBER OF BACKENDS
if [ "$NB_BACKENDS" == "1" ]; then
  echo "Scaling backends..."
  scalingo -a pass-culture-api scale web:"$NB_BACKENDS"
fi

# ADD CUSTOM DOMAIN NAME
# FIRST, YOU NEED TO GET A DNS (ASK IN "SLACK STARTUP D'ETAT")
if [ "$APP_CUSTOM_DNS" != "" ]; then
    echo "Registering new custom DNS..."
    scalingo -a "$APP_NAME" domains-add "$APP_CUSTOM_DNS"
fi


echo "Operation completed."