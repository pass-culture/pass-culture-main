#! /usr/bin/env bash -x

ENV="$1"
USER_ID="$2"
POD="$(kubectl get pod -n $ENV --field-selector status.phase=Running | rg -o "$ENV-pcapi-console-[\w-]+")"

CSV_OPTS="with delimiter ',' csv header"

exec_remote_query() {
    echo "$1" | kubectl -n $ENV exec -i $POD -- bash -c bin/pgcli-wrapper.sh # >/dev/null 2>&1
}

exec_local_query() {
    echo "$1" | docker exec -i pc-flask bash -c bin/pgcli-wrapper.sh # >/dev/null 2>&1
}

fetch_remote_file() {
    kubectl cp -n $ENV "$POD:/usr/src/app/$1" "$1"  # >/dev/null 2>&1
}

push_local_file() {
    docker cp "$1" "pc-postgres:/home/circleci/project/"
}

u_csv="u_$USER_ID.csv"
bfc_csv="bfc_$USER_ID.csv"
bfr_csv="bfr_$USER_ID.csv"
d_csv="d_$USER_ID.csv"

export_u_query="\copy (select * from \"user\" where id = $USER_ID) to '$u_csv' $CSV_OPTS"
export_bfc_query="\copy (select * from beneficiary_fraud_check where \"userId\" = $USER_ID) to '$bfc_csv' $CSV_OPTS"
export_bfr_query="\copy (select * from beneficiary_fraud_review where \"userId\" = $USER_ID) to '$bfr_csv' $CSV_OPTS"
export_d_query="\copy (select * from deposit where \"userId\" = $USER_ID) to '$d_csv' $CSV_OPTS"

import_u_query="copy \"user\" from '/home/circleci/project/$u_csv' $CSV_OPTS;"
import_bfc_query="copy beneficiary_fraud_check from '/home/circleci/project/$bfc_csv' $CSV_OPTS;"
import_bfr_query="copy beneficiary_fraud_review from '/home/circleci/project/$bfr_csv' $CSV_OPTS;"
import_d_query="copy deposit from '/home/circleci/project/$d_csv' $CSV_OPTS;"

exec_remote_query "$export_u_query"\
&&\
exec_remote_query "$export_bfc_query"\
&&\
exec_remote_query "$export_bfr_query"\
&&\
exec_remote_query "$export_d_query"\


fetch_remote_file "$u_csv"\
&&\
fetch_remote_file "$bfc_csv"\
&&\
fetch_remote_file "$bfr_csv"\
&&\
fetch_remote_file "$d_csv"\


push_local_file "$u_csv"\
&&\
push_local_file "$bfc_csv"\
&&\
push_local_file "$bfr_csv"\
&&\
push_local_file "$d_csv"


exec_local_query "$import_u_query"\
&&\
exec_local_query "$import_bfc_query"\
&&\
exec_local_query "$import_bfr_query"\
&&\
exec_local_query "$import_d_query"
