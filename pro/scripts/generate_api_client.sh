#!/usr/bin/env bash
openapi --input https://backend.testing.passculture.team/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient  --request ./scripts/customRequest.ts
openapi --input https://backend.testing.passculture.team/v2/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2  --request ./scripts/customRequest.ts
openapi --input https://backend.testing.passculture.team/adage-iframe/openapi.json --output src/apiClient/adage --indent='2' --name AppClientAdage --request ./scripts/customRequest.ts