#!/bin/bash
#
# A wrapper around pgcli that:
# - loads our "etc/pgcli.ini" configuration file;
# - defaults to $DATABASE_URL if no argument is given;
# - sets a colored prompt that clearly distinguishes when you're on
#   your development machine or on production.
#

# Default to $DATABASE_URL if no argument is given.
args="$*"
if [ $# -eq 0 ]; then args="${DATABASE_URL} "; fi

# Determine color of the prompt, depending on the environment.
environment=$(hostname | cut -d"-" -f1)
if [ "${environment}" == "production" ]; then color="\x1b[1;49;31m" # red
elif [ "${environment}" == "staging" ]; then color="\x1b[1;49;35m" # purple
elif [ "${environment}" == "testing" ]; then color="\x1b[1;49;36m" # cyan
else color=""; fi
color_reset="\x1b[0m"
prompt="${color}${environment}>${color_reset} "

config_path="$(dirname $0)/../etc/pgcli.ini"

# `--prompt` is manually added here, I don't know how to properly
# quote it to include the trailing space.
pgcli ${args} --prompt "${prompt}" --pgclirc "${config_path}"
