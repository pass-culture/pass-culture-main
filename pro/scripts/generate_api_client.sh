#!/usr/bin/env bash
set -e

docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate \
        -l typescript-fetch `# client type` \
        -i https://backend.passculture-testing.beta.gouv.fr/apidoc/openapi.json `# schema location` \
        -c /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        -t /local/swagger_codegen/gen_templates `# templates directory` \
        -o /local/src/api/v1/gen `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client for public v1 api and interfaces were generated successfully."

docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate \
        -l typescript-fetch `# client type` \
        -i https://backend.passculture-testing.beta.gouv.fr/v2/openapi.json `# schema location` \
        -c /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        -t /local/swagger_codegen/gen_templates `# templates directory` \
        -o /local/src/api/v2/gen `# output directory`

success "TypeScript API client for public v2 api and interfaces were generated successfully."

