#!/bin/bash

function test_backend {
    if [[ $# == 0 ]]; then
        PYTEST_ARGS="tests"
    else
        PYTEST_ARGS=$*
    fi
    RUN='docker stop pc-postgres-pytest;
        docker rm pc-postgres-pytest;
        docker-compose -f docker-compose-app.yml up -d postgres-test;
        docker exec pc-flask bash -c "cd /opt/services/flaskapp/src/ && rm -rf static/object_store_data/thumbs/* && PYTHONPATH=. pytest --color=yes -rsx -v $PYTEST_ARGS"'

}