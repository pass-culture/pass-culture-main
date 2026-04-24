#!/bin/bash

function test_backend {
  local pytest_args="${*:-tests}"
  docker stop pc-postgres-pytest
  docker rm -v pc-postgres-pytest
  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" up -d postgres-test
  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" build pcapi-tests --build-arg="network_mode=${DOCKER_NETWORK_MODE:-default}" --build-arg="uid=$UID"

  until docker compose -f "$ROOT_PATH/docker-compose-backend.yml" logs postgres-test 2>/dev/null | grep -q "PostgreSQL init process complete; ready for start up."; do
    echo "waiting for test-database"
    sleep 0.5
  done

  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" run --rm \
    -e RUN_ENV=tests -e SQLALCHEMY_WARN_20=1 \
    pcapi-tests \
    bash -c "rm -rf static/object_store_data/thumbs* && \
             pytest -m 'not backoffice' --durations=5 --color=yes -rsx -v $pytest_args"
}

function test_backoffice {
  local pytest_args="${*:-tests}"
  docker stop pc-postgres-pytest
  docker rm -v pc-postgres-pytest
  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" up -d postgres-test
  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" build pcapi-tests --build-arg="network_mode=${DOCKER_NETWORK_MODE:-default}" --build-arg="uid=$UID"

  until docker compose -f "$ROOT_PATH/docker-compose-backend.yml" logs postgres-test 2>/dev/null | grep -q "PostgreSQL init process complete; ready for start up."; do
    echo "waiting for test-database"
    sleep 0.5
  done

  docker compose -f "$ROOT_PATH/docker-compose-backend.yml" run --rm -e RUN_ENV=tests -e SQLALCHEMY_WARN_20=1 \
    pcapi-tests \
    bash -c "rm -rf static/object_store_data/thumbs* && \
             pytest -m backoffice --durations=5 --color=yes -rsx -v $pytest_args"
}
