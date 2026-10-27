#!/bin/bash

set -eu

function create_db_and_user() {
    local db_name=$1
    echo "Processing database and user '$db_name'"

    # 1. Create User (Idempotent: ignores "already exists" error)
    # We use a DO block to catch the duplicate_object error
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
        DO \$\$
        BEGIN
            CREATE ROLE $db_name WITH LOGIN PASSWORD '$db_name' NOSUPERUSER NOCREATEDB;
        EXCEPTION WHEN duplicate_object THEN
            RAISE NOTICE 'Role % already exists, skipping create.', '$db_name';
        END
        \$\$;
EOSQL

    # 2. Create Database (Idempotent: checks pg_database first)
    # We check if the DB exists in the system catalog before trying to create it.
    if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$db_name'" | grep -q 1; then
        echo "  Database '$db_name' already exists. Skipping."
    else
        echo "  Creating database '$db_name'..."
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
            CREATE DATABASE $db_name OWNER $db_name;
            GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_name;
EOSQL
    fi
}

if [ -n "$POSTGRES_DBS" ]; then
    echo "Multiple database creation requested: $POSTGRES_DBS"

    # Split the comma-separated variable into an array and iterate
    for db in $(echo $POSTGRES_DBS | tr ',' ' '); do
        create_db_and_user $db
    done

    echo "Multiple databases processed"
fi
