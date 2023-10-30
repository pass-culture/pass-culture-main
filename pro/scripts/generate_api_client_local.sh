#!/usr/bin/env bash
set -e
openapi --input http://localhost/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient --request ./scripts/customRequest.ts
openapi --input http://localhost/v2/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2 --request ./scripts/customRequest.ts
openapi --input http://localhost/adage-iframe/openapi.json --output src/apiClient/adage --indent='2' --name AppClientAdage --request ./scripts/customRequest.ts