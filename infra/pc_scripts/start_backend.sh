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

    if _is_proxy_running; then
        if ! _is_proxy_cert_copied; then
            echo "Proxy certificate not found in api folder."
            echo "Please copy it first in api folder as 'cacert.pem'"
            exit
        fi

        RUN="$RUN --build-arg=\"network_mode=proxy\""
    fi

    RUN="$RUN"
}

function start_backend {
    concat_command
    RUN="$RUN docker compose -f $ROOT_PATH/docker-compose-backend.yml up --watch"
    if  [[ $SLOW == true ]];then
        RUN="$RUN --force-recreate"
    fi
}

function drop_data {
    concat_command
    RUN="$RUN rm -rf '$ROOT_PATH/api/static/object_store_data' && docker compose -f '$ROOT_PATH/docker-compose-backend.yml' down --volumes"
}

function rebuild_backend {
    concat_command
    drop_data
    concat_command
    build_backend "--no-cache"
}

