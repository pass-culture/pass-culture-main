#!/env/bash

function start_metabase {
    RUN='cd $ROOT_PATH && docker-compose -f "$ROOT_PATH"/docker-compose-metabase.yml up'
}

function restart_metabase {
    RUN='docker-compose -f "$ROOT_PATH"/docker-compose-metabase.yml down --volumes;
    cd "$ROOT_PATH" && docker-compose -f "$ROOT_PATH"/docker-compose-metabase.yml up --force-recreate'
}