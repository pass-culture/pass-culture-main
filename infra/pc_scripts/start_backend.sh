#!/bin/bash

function start_backend {
    RUN='cd $ROOT_PATH && docker-compose -f docker-compose-app.yml pull flask && docker-compose -f docker-compose-app.yml up'
}

function restart_backend {
    RUN='sudo rm -rf "$ROOT_PATH"/api/static/object_store_data;
    docker-compose -f docker-compose-app.yml down --volumes;
    cd "$ROOT_PATH" && docker-compose -f docker-compose-app.yml pull && docker-compose -f docker-compose-app.yml up --force-recreate'
}
