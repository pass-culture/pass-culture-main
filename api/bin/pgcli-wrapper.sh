#!/bin/bash
#
# A wrapper around pgcli that:
# - defaults to $DATABASE_URL if no argument is given;
# - disables automatic LIMIT;
# - disables startup and exit messages;
# - sets a colored prompt that clearly distinguishes when you're on
#   your development machine or on production.
#

# Default to $DATABASE_URL if no argument is given.
args="$*"
if [ $# -eq 0 ]; then args="${DATABASE_URL} "; fi

# Disable automatic LIMIT.
# This may be an nice feature when you're used to pgcli. Otherwise,
# you may very well miss the warning (especially if the SQL query is
# fast) and not notice that the output was cropped to 1000 rows (which
# is the default).
args+=" --row-limit 0"

# Disable startup and exit messages.
args+=" --less-chatty"

# Determine color of the prompt, depending on the environment.
environment=$(hostname | cut -d"-" -f1)
if [ "${environment}" == "production" ]; then color="\x1b[1;49;31m" # red
elif [ "${environment}" == "staging" ]; then color="\x1b[1;49;35m" # purple
elif [ "${environment}" == "testing" ]; then color="\x1b[1;49;36m" # cyan
else color=""; fi
color_reset="\x1b[0m"
prompt="${color}${environment}>${color_reset} "

# `--prompt` is manually added here, I don't know how to properly
# quote it to include the trailing space.
pgcli ${args} --prompt "${prompt}"
