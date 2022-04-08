#!/usr/bin/env bash

# see documentation: https://openapi-generator.tech/docs/debugging/

set -e

docker run --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  --enable-post-process-file \
  -g typescript-fetch \
  -c /local/openapi_generator/openapi_generator_config.json \
  -i /local/openapi_generator/test/input_data/openapi.json \
  -t /local/openapi_generator/templates \
  -o /local/openapi_generator/test/api/gen

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client for test api and interfaces were generated successfully."
