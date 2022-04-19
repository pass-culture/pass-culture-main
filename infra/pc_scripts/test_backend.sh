#!/bin/bash

function test_backend {
    if [[ $# == 0 ]]; then
        PYTEST_ARGS="tests"
    else
        PYTEST_ARGS=$*
    fi
    RUN='docker stop pc-postgres-pytest;
        docker rm pc-postgres-pytest;
        docker-compose -f "$ROOT_PATH"/docker-compose-app.yml up -d postgres-test;
        while ! docker-compose -f "$ROOT_PATH"/docker-compose-app.yml logs postgres-test 2> /dev/null | grep -q "PostgreSQL init process complete; ready for start up."; do echo "waiting for test-database"; sleep 0.5; done;
        rm -rf static/object_store_data/thumbs/* && RUN_ENV=tests pytest --durations=5 --color=yes -rsx -v -p no:warnings $PYTEST_ARGS
        '
}
