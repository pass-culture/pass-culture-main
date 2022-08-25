#!/usr/bin/env bash
openapi --input http://localhost:5001/adage-iframe/openapi.json --output src/apiClient --indent='2' --name AppClient
