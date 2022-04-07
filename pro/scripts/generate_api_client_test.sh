#!/usr/bin/env bash

# some interesting information can be found on a other project
# see https://openapi-generator.tech/docs/debugging/

set -e

# debug mode found here : https://github.com/swagger-api/swagger-codegen/wiki/FAQ
# -DdebugOperations=true
# -DdebugModels=true


docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate \
        -DdebugOperations=true \
        -l typescript-fetch `# client type` \
        -i /local/swagger_codegen/test/input_data/openapi.json `# schema location` \
        -c /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        -t /local/swagger_codegen/gen_templates `# templates directory` \
        -o /local/swagger_codegen/test/api/gen `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client for test api and interfaces were generated successfully."
