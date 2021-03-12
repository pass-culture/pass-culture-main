#!/bin/bash -e

# pcapi app expects a DATABASE_URL environment variable
export DATABASE_URL=${PUBLIC_DATABASE_URL}
export POSTGRES_CONNEXION_STRING_DEST=${PUBLIC_DATABASE_URL}
export DUMP_TIMESTAMPED_FILENAME="$(date +'%y-%m-%d')_${DUMP_FILENAME}"

function echo_time {
    date +'%H:%M:%S:%N'
}

function export_running_output {
    gcloud sql operations list \
    --instance ${POSTGRES_INSTANCE_SRC} \
    --filter TYPE=EXPORT \
    --filter STATUS=RUNNING \
    --format="value(name)"
}

function import_running_output {
    gcloud sql operations list \
    --instance ${POSTGRES_INSTANCE_DEST} \
    --project ${PROJECT_DEST} \
    --filter TYPE=IMPORT \
    --filter STATUS=RUNNING \
    --format="value(name)"
}

if [ "$EXPORT_DATA" = "true" ];then
    # Check is an opeation is already running on the instance
    # (export will fail is there is one)
    echo "Starting: gcloud sql operations list $(echo_time)"
    retries=5
    while [ $(export_running_output) != "" ];do
        if [ "${retries}" -gt 0 ];then
            let "retries-=1"
            echo "An operations in currently running on the instance; Retries left : ${retries}; waiting 5min"
            sleep 300
        else
            echo "An operations in currently running on the instance; Retries left : ${retries}; exiting"
            exit
        fi
    done
    echo "Ended: gcloud sql operations list $(echo_time)"

    # Export database in SQL format to encrypted bucket
    # Do not wait for answer as the operation might take some time and the connexion might drop
    echo "Starting: gcloud sql export $(echo_time)"
    gcloud sql export sql \
        ${POSTGRES_INSTANCE_SRC} gs://${DUMP_BUCKET_NAME}/${DUMP_TIMESTAMPED_FILENAME} \
        --database ${POSTGRES_DATABASE_SRC} \
        --offload \
        --async \
        --quiet
    echo "Ended: gcloud sql export $(echo_time)"

    # Check is dump file is present in bucket (which means the export operation is over)
    while ! gsutil ls gs://${DUMP_BUCKET_NAME}/${DUMP_TIMESTAMPED_FILENAME} 2>/dev/null;
    do
        echo "Dump file not found in bucket; Export in progress $(echo_time)";
        sleep 300
    done
fi

if [ "$RECREATE_DEST_DATABASE" = "true" ];then
    echo "Starting: psql terminate connections $(echo_time)"
    psql "${POSTGRES_CONNEXION_STRING_DEST}" \
        -c 'SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();'
    echo "Ending: psql terminate connections $(echo_time)"

    # Delete the destination database for clean start
    echo "Starting: gcloud sql database delete $(echo_time)"
    gcloud sql databases delete \
        ${POSTGRES_DATABASE_DEST} \
        --instance ${POSTGRES_INSTANCE_DEST} \
        --project ${PROJECT_DEST} \
        --quiet
    echo "Ended: gcloud database delete $(echo_time)"


    # Recreate the destination database
    echo "Starting: gcloud sql database create $(echo_time)"
    gcloud sql databases create \
        ${POSTGRES_DATABASE_DEST} \
        --instance ${POSTGRES_INSTANCE_DEST} \
        --project ${PROJECT_DEST} \
        --quiet
    echo "Ended: gcloud database create $(echo_time)"
fi

if [ "$IMPORT_DATA" = "true" ];then
    # Import the SQL dump to the destination database
    echo "Starting: gcloud sql import $(echo_time)"
    gcloud sql import sql \
        ${POSTGRES_INSTANCE_DEST} gs://${DUMP_BUCKET_NAME}/${DUMP_TIMESTAMPED_FILENAME} \
        --database ${POSTGRES_DATABASE_DEST} \
        --user ${POSTGRES_USER_DEST} \
        --project ${PROJECT_DEST} \
        --async \
        --quiet
    echo "Ended: gcloud sql import $(echo_time)"

    # Check is an operation is still running on the instance before continuing
    echo "Starting: gcloud sql operations list $(echo_time)"
    import_running_output=""
    until [ "$import_running_output" = "" ]
    do
        import_running_output=$(import_running_output)
        echo "Import operations currently running:\n $import_running_output"
        sleep 300
    done
    echo "Ended: gcloud sql operations list $(echo_time)"
fi

if [ "$POSTGRES_REMOVE_UNNEEDED_TABLES" = "true" ];then
    echo "Starting: pruning staging database $(echo_time)"
    for TABLE in ${POSTGRES_UNNEEDED_TABLES};do
        execution=$(psql "${POSTGRES_CONNEXION_STRING_DEST}" \
            --echo-errors \
            -c "TRUNCATE TABLE ${TABLE};" 2>&1)
        if [ "${execution}" != "TRUNCATE TABLE" ];then
            echo "Pruning ${TABLE} failed : error found"
            echo "${execution}"
        fi
    done
    echo "Ended: pruning staging database $(echo_time)"
fi

if [ "$DELETE_DUMP_AFTER_IMPORT" = "true" ];then
    # Delete the SQL dump in the bucket
    echo "Starting: gsutil rm $(echo_time)"
    gsutil rm gs://${DUMP_BUCKET_NAME}/${DUMP_TIMESTAMPED_FILENAME}
    echo "Ended: gsutil rm $(echo_time)"
fi

if [ "$ANONYMISE_DEST" = "true" ];then
    # Launch anonymization SQL script
    echo "Starting: psql anonymize script $(echo_time)"
    sed -i "s|##PASSWORD##|${DATABASE_ANONYMIZED_PASSWORD}|" ${POSTGRES_SCRIPT_PATH}
    psql "${POSTGRES_CONNEXION_STRING_DEST}" \
        --echo-errors \
        --file=${POSTGRES_SCRIPT_PATH}
    echo "Ended: psql anonymize script $(echo_time)"
fi

if [ "$CREATE_USERS" = "true" ];then
    # Launch import user script
    echo "Starting: python3 $(echo_time)"
    python3 ${PC_API_ROOT_PATH}/${IMPORT_USERS_SCRIPT_PATH} ${USERS_CSV_PATH}
    echo "Ended: python3 $(echo_time)"
fi
