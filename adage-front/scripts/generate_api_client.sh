#!/usr/bin/env bash
openapi --input https://backend.testing.passculture.team/adage-iframe/openapi.json --output src/apiClient --indent='2' --name AppClient 
