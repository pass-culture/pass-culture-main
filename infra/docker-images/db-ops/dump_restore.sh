#!/bin/bash -e

# pcapi app expects a DATABASE_URL environment variable
export DATABASE_URL=${PUBLIC_DATABASE_URL}
export POSTGRES_CONNEXION_STRING_DEST=${PUBLIC_DATABASE_URL}

if [ "$EXPORT_DATA" = "true" ];then
    # Check is an opeation is already running on the instance
    # (export will fail is there is one)
    echo "Starting: gcloud sql operations list"
    export_running_output=$(gcloud sql operations list \
                --instance ${POSTGRES_INSTANCE_SRC} \
                --filter TYPE=EXPORT \
                --filter STATUS=RUNNING 2>&1)
    echo "Ended: gcloud sql operations list"

    if [ "$export_running_output" = "Listed 0 items." ]; then
        echo "No operation currently running on the instance; Continuing";
    else
        echo "An operations in currently running on the instance; Stopping"
        exit
    fi

    # Export database in SQL format to encrypted bucket
    # Do not wait for answer as the operation might take some time and the connexion might drop
    echo "Starting: gcloud sql export"
    gcloud sql export sql \
        ${POSTGRES_INSTANCE_SRC} gs://${DUMP_BUCKET_NAME}/${DUMP_BUCKET_PATH} \
        --database ${POSTGRES_DATABASE_SRC} \
        --offload \
        --async \
        --quiet
    echo "Ended: gcloud sql export"

    # Check is dump file is present in bucket (which means the export operation is over)
    while ! gsutil ls gs://${DUMP_BUCKET_NAME}/${DUMP_BUCKET_PATH} 2>/dev/null;
    do
        echo "Dump file not found in bucket; Export in progress";
        sleep 300
    done
fi

if [ "$RECREATE_DEST_DATABASE" = "true" ];then
    echo "Starting: psql terminate connections"
    psql "${POSTGRES_CONNEXION_STRING_DEST}" \
        -c 'SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();'
    echo "Ending: psql terminate connections"

    # Delete the destination database for clean start
    echo "Starting: gcloud sql database delete"
    gcloud sql databases delete \
        ${POSTGRES_DATABASE_DEST} \
        --instance ${POSTGRES_INSTANCE_DEST} \
        --project ${PROJECT_DEST} \
        --quiet
    echo "Ended: gcloud database delete"


    # Recreate the destination database
    echo "Starting: gcloud sql database create"
    gcloud sql databases create \
        ${POSTGRES_DATABASE_DEST} \
        --instance ${POSTGRES_INSTANCE_DEST} \
        --project ${PROJECT_DEST} \
        --quiet
    echo "Ended: gcloud database create"
fi

if [ "$IMPORT_DATA" = "true" ];then
    # Import the SQL dump to the destination database
    echo "Starting: gcloud sql import"
    gcloud sql import sql \
        ${POSTGRES_INSTANCE_DEST} gs://${DUMP_BUCKET_NAME}/${DUMP_BUCKET_PATH} \
        --database ${POSTGRES_DATABASE_DEST} \
        --user ${POSTGRES_USER_DEST} \
        --project ${PROJECT_DEST} \
        --async \
        --quiet
    echo "Ended: gcloud sql import"

    # Check is an operation is still running on the instance before continuing
    echo "Starting: gcloud sql operations list"
    import_running_output=""
    until [ "$import_running_output" = "Listed 0 items." ]
    do
        import_running_output=$(gcloud sql operations list \
                --instance ${POSTGRES_INSTANCE_DEST} \
                --project ${PROJECT_DEST} \
                --filter TYPE=IMPORT \
                --filter STATUS=RUNNING 2>&1)
        echo "Import operations currently running:\n $import_running_output"
        sleep 300
    done
    echo "Ended: gcloud sql operations list"
fi

if [ "$DELETE_DUMP_AFTER_IMPORT" = "true" ];then
    # Delete the SQL dump in the bucket
    echo "Starting: gsutil rm"
    gsutil rm gs://${DUMP_BUCKET_NAME}/${DUMP_BUCKET_PATH}
    echo "Ended: gsutil rm"
fi


if [ "$ANONYMISE_DEST" = "true" ];then
    # Launch anonymization SQL script
    sed -i "s|##PASSWORD##|${DATABASE_ANONYMIZED_PASSWORD}|" ${POSTGRES_SCRIPT_PATH}
    echo "Starting: psql anonymize script"
    psql "${POSTGRES_CONNEXION_STRING_DEST}" \
        --echo-errors \
        --file=${POSTGRES_SCRIPT_PATH}
    echo "Ended: psql anonymize script"
fi

if [ "$CREATE_USERS" = "true" ];then
    # Launch import user script
    echo "Starting: python3"
    python3 ${PC_API_ROOT_PATH}/${IMPORT_USERS_SCRIPT_PATH} ${USERS_CSV_PATH}
    echo "Ended: python3"
fi

if [ "$POSTGRES_REMOVE_UNNEEDED_TABLES" = "true" ];then
    echo "Starting: pruning staging database"
    for TABLE in ${POSTGRES_UNNEEDED_TABLES};do
        execution=$(psql "${POSTGRES_CONNEXION_STRING_DEST}" \
            --echo-errors \
            -c "TRUNCATE TABLE ${TABLE};" 2>&1)
        if [ "${execution}" != "TRUNCATE TABLE" ];then
            echo "Pruning ${TABLE} failed : error found"
            echo "${execution}"
        fi
    done
    echo "Ended: pruning staging database"
fi
