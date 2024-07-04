#!/bin/bash

function test_backend {
    if [[ $# == 0 ]]; then
        PYTEST_ARGS="tests"
    else
        PYTEST_ARGS=$*
    fi
    RUN='docker stop pc-postgres-pytest;
        docker rm -v pc-postgres-pytest;
        docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml up -d postgres-test;
        while ! docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml logs postgres-test 2> /dev/null | grep -q "PostgreSQL init process complete; ready for start up."; do echo "waiting for test-database"; sleep 0.5; done;
        docker exec -it pc-api bash -c "cd /usr/src/app/ && rm -rf static/object_store_data/thumbs/* && RUN_ENV=tests SQLALCHEMY_WARN_20=1 pytest -m \"not backoffice\" --durations=5 --color=yes -rsx -v $PYTEST_ARGS"
        '
}

function test_backoffice {
    if [[ $# == 0 ]]; then
        PYTEST_ARGS="tests"
    else
        PYTEST_ARGS=$*
    fi
    RUN='docker stop pc-postgres-pytest;
        docker rm -v pc-postgres-pytest;
        docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml up -d postgres-test;
        while ! docker-compose -f "$ROOT_PATH"/docker-compose-backend.yml logs postgres-test 2> /dev/null | grep -q "PostgreSQL init process complete; ready for start up."; do echo "waiting for test-database"; sleep 0.5; done;
        docker exec -it pc-backoffice bash -c "cd /usr/src/app/ && rm -rf static/object_store_data/thumbs/* && RUN_ENV=tests SQLALCHEMY_WARN_20=1 pytest -m backoffice --durations=5 --color=yes -rsx -v $PYTEST_ARGS"
        '
}
