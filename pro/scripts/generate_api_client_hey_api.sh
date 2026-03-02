#!/usr/bin/env bash
set -e

npx @hey-api/openapi-ts -f openapi-ts.config.ts
npx biome check --write src/apiClient/hey-api/
