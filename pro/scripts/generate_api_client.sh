#!/usr/bin/env bash
openapi --input https://backend.passculture-testing.beta.gouv.fr/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient 
openapi --input https://backend.passculture-testing.beta.gouv.fr/v2/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2
