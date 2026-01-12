#!/usr/bin/env bash
set -e

PCAPI_HOST=${PCAPI_HOST:-"localhost"}
swagger-typescript-api generate --path http://${PCAPI_HOST}/pro/openapi.json --output ./src/apiClient --modular
openapi --input http://${PCAPI_HOST}/adage-iframe/openapi.json --output src/apiClient/adage --indent='2' --name AppClientAdage --request ./scripts/customRequest.ts
