#!/bin/bash

function concat_command {
    if [[ "$RUN" != "" ]] && [[ "$RUN" != *\&\& ]]; then
        RUN="$RUN &&"
    fi
}

function move {
    concat_command
    RUN="$RUN cd '$ROOT_PATH'"
}

function build_backend {
    concat_command
    move
    concat_command
    if  [[ $FAST != true ]];then
        RUN="$RUN docker compose -f '$ROOT_PATH/docker-compose-backend.yml' build --build-arg=\"uid=$UID\""
    fi
}

function build_proxy_backend {
    concat_command
    move
    concat_command
    if  [[ $FAST != true ]];then
        RUN="$RUN docker compose -f '$ROOT_PATH/docker-compose-backend.yml' build --build-arg=\"network_mode=proxy\" --build-arg=\"uid=$UID\""
    fi
}

function start_backend {
    concat_command
    RUN="$RUN docker compose -f $ROOT_PATH/docker-compose-backend.yml up"
    if  [[ $SLOW == true ]];then
        RUN="$RUN --force-recreate"
    fi
}

function drop_data {
    concat_command
    RUN="$RUN sudo rm -rf '$ROOT_PATH/api/static/object_store_data' && docker compose -f '$ROOT_PATH/docker-compose-backend.yml' down --volumes"
}

function rebuild_backend {
    RUN='docker compose -f "$ROOT_PATH"/docker-compose-backend.yml build --no-cache --build-arg=\"uid=$UID\";
    sudo rm -rf $ROOT_PATH/api/static/object_store_data;
    docker compose -f "$ROOT_PATH"/docker-compose-backend.yml down --volumes'
}

