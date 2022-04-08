#!/usr/bin/env bash

# see documentation: https://openapi-generator.tech/docs/debugging/

set -e

docker run --network="host" --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -g typescript-fetch \
  -c /local/openapi_generator/openapi_generator_config.json \
  -i http://localhost/pro/openapi.json \
  -t /local/openapi_generator/templates \
  -o /local/src/api/openapi_generator/v1/gen

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client for test api and interfaces were generated successfully."

# Manualy fix error on build, wait for openapitool to be fixed.
# [main] WARN  o.o.c.l.AbstractTypeScriptClientCodegen - The import is a union type. Consider using the toModelImportMap method.
# https://github.com/OpenAPITools/openapi-generator/blob/master/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/AbstractTypeScriptClientCodegen.java
git grep -rl "from.*'.\/number \| string';$" src/api/openapi_generator/ | xargs perl -0777 -i -pe "s/import [\w\{\}\s\|,]+ '.\/number \| string';\n//smg"
success "Wrong import have been cleaned."