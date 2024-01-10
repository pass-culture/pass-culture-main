#!/usr/bin/env bash
set -e
openapi --input http://0.0.0.0:5001/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient --request ./scripts/customRequest.ts
openapi --input http://0.0.0.0:5001/v2/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2 --request ./scripts/customRequest.ts
openapi --input http://0.0.0.0:5001/adage-iframe/openapi.json --output src/apiClient/adage --indent='2' --name AppClientAdage --request ./scripts/customRequest.ts
