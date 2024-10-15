#!/usr/bin/env bash
set -e

PCAPI_HOST=${PCAPI_HOST:-"localhost"}
openapi --input http://${PCAPI_HOST}/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient --request ./scripts/customRequest.ts
openapi --input http://${PCAPI_HOST}/v2/deprecated/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2 --request ./scripts/customRequest.ts
openapi --input http://${PCAPI_HOST}/adage-iframe/openapi.json --output src/apiClient/adage --indent='2' --name AppClientAdage --request ./scripts/customRequest.ts
