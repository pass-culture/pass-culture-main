#!/bin/bash

API_DIR="$ROOT_PATH/api"
RUN="${RUN:=''}" # avoid unbound variable error

# Recreate databases
recreate_database() {
    psql <<EOF
    \echo recreating pass_culture database with UTC timezone
    \set ON_ERROR_STOP on
    DROP DATABASE IF EXISTS pass_culture;
    CREATE DATABASE pass_culture WITH OWNER pass_culture;
    \c pass_culture
    CREATE EXTENSION IF NOT EXISTS postgis;
    ALTER DATABASE pass_culture SET TIMEZONE TO 'UTC';
EOF
}
recreate_database_test() {
    psql <<EOF
    \echo recreating pass_culture_test database with UTC timezone
    \set ON_ERROR_STOP on
    DROP DATABASE IF EXISTS pass_culture_test;
    CREATE DATABASE pass_culture_test WITH OWNER pytest;
    \c pass_culture_test
    CREATE EXTENSION IF NOT EXISTS postgis;
    ALTER DATABASE pass_culture_test SET TIMEZONE TO 'UTC';
EOF
}

check_requirements() {
    # check poetry is installed
    if ! command -v python &> /dev/null; then
        echo "Error: Python not found. Run poetry shell"
        return 1
    fi

    # Check Redis is started
    if ! command -v redis-cli &> /dev/null; then
        echo "Error: redis-cli not found. Please install Redis."
        return 1
    fi

    if ! redis-cli ping | grep -q "PONG"; then
        echo "Error: Redis is not running."
        return 1
    fi
}

# Run migrations + install Feature flags + start API
start_api_no_docker() {
    if ! check_requirements; then
        return 1
    fi
    cd $API_DIR && $API_DIR/start-api-when-database-is-ready.sh
}

# Starts backoffice
start_backoffice_no_docker() {
    if ! check_requirements; then
        return 1
    fi
    cd $API_DIR && while true; do python src/pcapi/backoffice_app.py || continue; done
}

# Clears DB and run industrial sandbox
restart_api_no_docker() {
printf "Cette commande va supprimer les bases de données et relancer la sandbox. Confirmer? [Y/n] "
    if ! check_requirements; then
        return 1
    fi
    read -r response
    response=${response:-Y}
    case $response in
        [Yy]*)
            cd $API_DIR
            recreate_database \
            && recreate_database_test \
            && flask install_postgres_extensions \
            && alembic upgrade pre@head \
            && alembic upgrade post@head \
            && flask install_data \
            && flask sandbox -n industrial \
            && $API_DIR/start-api-when-database-is-ready.sh \
            ;;
        *)
            echo "Exécution annulée."
            ;;
    esac
}

# Setup
setup_no_docker() {
    cd $API_DIR
    if ! check_requirements; then
        echo "Requirements check failed. Exiting setup."
        return 1
    fi
    passculture_db="DATABASE_URL=postgresql://pass_culture:passq@localhost:5432/pass_culture"
    passculture_test_db="DATABASE_URL_TEST=postgresql://pytest:pytest@localhost:5432/pass_culture_test"
    backoffice_port="FLASK_BACKOFFICE_PORT=5002"
    flask_ip="FLASK_IP=::1"
    secret_file="$API_DIR/.env.local.secret"
    if ! grep -qF "$passculture_db" "$secret_file"; then
        echo "$passculture_db" >> "$secret_file"
    fi
    if ! grep -qF "$passculture_test_db" "$secret_file"; then
        echo "$passculture_test_db" >> "$secret_file"
        
    fi
    if ! grep -qF "$backoffice_port" "$secret_file"; then
        echo "$backoffice_port" >> "$secret_file"
    fi
    if ! grep -qF "$flask_ip" "$secret_file"; then
        echo "$flask_ip" >> "$secret_file"
    fi
    recreate_database
    recreate_database_test
    flask install_postgres_extensions
    alembic upgrade pre@head
    alembic upgrade post@head
}