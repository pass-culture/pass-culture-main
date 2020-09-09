#!/bin/bash

function start_backend {
    RUN='cd "$ROOT_PATH" && docker-compose pull flask && docker-compose up'
}

function restart_backend {
    RUN='cd "$ROOT_PATH" && sudo rm -rf api/static/object_store_data;
    docker-compose down --volumes;
    docker-compose pull && docker-compose up --force-recreate'
}

function rebuild_backend {
    RUN='cd "$ROOT_PATH" && docker-compose build --no-cache;
    sudo rm -rf api/static/object_store_data;
    docker-compose down --volumes'
}
