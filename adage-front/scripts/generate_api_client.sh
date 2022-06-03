#!/usr/bin/env bash
set -e

docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate \
        -l typescript-fetch `# client type` \
        -i https://backend.testing.passculture.team/adage-iframe/openapi.json `# schema location` \
        -c /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        -t /local/swagger_codegen/gen_templates `# templates directory` \
        -o /local/src/api/gen `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client for adage-iframe api and interfaces were generated successfully."
