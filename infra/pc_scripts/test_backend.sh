#!/bin/bash

function test_backend {
    if [[ $# == 0 ]]; then
        PYTEST_ARGS="tests"
    else
        PYTEST_ARGS=$*
    fi
    RUN='docker stop pc-postgres-pytest;
        docker rm -v pc-postgres-pytest;
        docker-compose -f "$ROOT_PATH"/docker-compose-app.yml up -d postgres-test;
        while ! docker-compose -f "$ROOT_PATH"/docker-compose-app.yml logs postgres-test 2> /dev/null | grep -q "listening on IPv4 address"; do echo "waiting for test-database"; sleep 0.5; done;
        docker exec -it pc-flask bash -c "cd /usr/src/app/ && rm -rf static/object_store_data/thumbs/* && RUN_ENV=tests pytest --durations=5 --color=yes -rsx -v $PYTEST_ARGS"
        '
}
