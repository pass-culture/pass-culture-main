#!/bin/bash

function start_backend {
    docker_compose_major=$(docker-compose -v 2>&1 | sed "s/.*version v*\([0-9]\).\([0-9]*\).\([0-9]*\).*/\1/");
    docker_compose_minor=$(docker-compose -v 2>&1 | sed "s/.*version v*\([0-9]\).\([0-9]*\).\([0-9]*\).*/\2/");
    if [ "$docker_compose_major" -le "1" ] && [ "$docker_compose_minor" -le "23" ]; then
        echo "This script requires docker-compose 1.24 or greater"
        exit 1
    fi
    RUN='cd $ROOT_PATH && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml build && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml up'
}

function start_proxy_backend {
    RUN='cd $ROOT_PATH && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml build --build-arg="network_mode=proxy" && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml up'
}

function restart_backend {
    RUN='sudo rm -rf "$ROOT_PATH"/api/static/object_store_data;
    docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml down --volumes;
    cd "$ROOT_PATH" && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml build && docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml up --force-recreate'
}

function rebuild_backend {
    RUN='docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml build --no-cache;
    sudo rm -rf $ROOT_PATH/api/static/object_store_data;
    docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml down --volumes'
}
