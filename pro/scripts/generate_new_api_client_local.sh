#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

GREEN='\033[0;32m'
NO_COLOR='\033[0m'

docker run \
    --network="host" \
    --rm \
    --volume "${PWD}:/local" \
    "swaggerapi/swagger-codegen-cli-v3:${SWAGGER_CODEGEN_CLI_VERSION:-'latest'}" generate \
        --input-spec http://localhost:5001/pro/openapi.json `# schema location` \
        --lang typescript-fetch `# client type` \
        --config /local/src/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        --template-dir /local/src/swagger_codegen/gen_templates `# templates directory` \
        --output /local/src/api/gen `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client and interfaces were generated successfully."
