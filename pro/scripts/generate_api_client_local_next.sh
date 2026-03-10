#!/usr/bin/env bash
set -e

export PCAPI_HOST=${PCAPI_HOST:-"localhost:5001"}

echo "Generating v1 (Pro) API client from http://${PCAPI_HOST}/pro/openapi.json..."
./node_modules/.bin/openapi-ts -f config/openapi-ts.v1.config.ts

echo "Generating adage API client from http://${PCAPI_HOST}/adage-iframe/openapi.json..."
./node_modules/.bin/openapi-ts -f config/openapi-ts.adage.config.ts

echo "Done."
