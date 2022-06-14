#!/bin/bash

# This bash script calls sendinblue_batch_update_user_attributes.py script for chunks of users.
# It replaces batch_update_users_attributes.py which is killed in production environment because of memory usage.
# Use this loop as long as memory issue is not fixed in the original script.

# Run on production pod:
# bash src/pcapi/scripts/external_users/sendinblue_batch_update_users_loop.sh
# bash src/pcapi/scripts/external_users/sendinblue_batch_update_users_loop.sh >> /tmp/batch_loop_$(date -I).log 2>&1 &

export PYTHONPATH=src

MAX_USER_ID=$(python "$(dirname $0)/max_user_id.py")
MIN_USER_ID=0
CHUNK_SIZE=500

for MAX_ID in $(seq ${MAX_USER_ID} -${CHUNK_SIZE} ${MIN_USER_ID}); do
  MIN_ID=$((${MAX_ID} - ${CHUNK_SIZE} + 1))
  if [ ${MIN_ID} -lt ${MIN_USER_ID} ] ; then
      MIN_ID=${MIN_USER_ID}
  fi
  echo "$(dirname $0)/sendinblue_batch_update_user_attributes.py" ${MIN_ID} ${MAX_ID}
  python "$(dirname $0)/sendinblue_batch_update_user_attributes.py" ${MIN_ID} ${MAX_ID}
done
