#!/usr/bin/env bash
set -e

docker run --network="host" --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate \
        -l typescript-fetch `# client type` \
        -i http://localhost/apidoc/openapi.json `# schema location` \
        -c /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        -t /local/swagger_codegen/gen_templates `# templates directory` \
        -o /local/src/api/gen `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client and interfaces were generated successfully."
