#!/usr/bin/env bash
openapi --input http://localhost/pro/openapi.json --output src/apiClient/v1 --indent='2' --name AppClient 
openapi --input http://localhost/v2/openapi.json --output src/apiClient/v2 --indent='2' --name AppClientV2