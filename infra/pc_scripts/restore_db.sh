#!/bin/bash

function restore_db_intact {
    confirm "Warning: your database will be wiped. Is this OK ?"
    if [[ $# == 0 ]]; then
        echo "Usage : pc restore-db-intact <backup_file> [arguments]"
        exit
    fi
    local backup_file="$1"
    RUN='source "$ROOT_PATH"/env_file;
        PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1
                                    --port 5434
                                    --username "$POSTGRES_USER"
                                    --dbname "$POSTGRES_DB"
                                    -a -f "$ROOT_PATH"/infra/scalingo/clean_database.sql;
        cat "'$backup_file'" | docker exec -i pc-postgres pg_restore -d pass_culture -U pass_culture -c'
}
