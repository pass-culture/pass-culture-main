#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

GREEN='\033[0;32m'
NO_COLOR='\033[0m'
PCAPI_HOST=${PCAPI_HOST:-"localhost:5001"}

docker run \
    --network="host" \
    --rm \
    --volume "${PWD}:/local" \
    swaggerapi/swagger-codegen-cli-v3:latest generate \
        --verbose [] \
        --additional-properties=enumPropertyNaming=original,modelPropertyNaming=original,removeEnumValuePrefix=false \
        --input-spec http://${PCAPI_HOST}/pro/openapi.json `# schema location` \
        --lang typescript-fetch `# client type` \
        --config /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        --template-dir /local/swagger_codegen/gen_templates `# templates directory` \
        --output /local/src/apiClient/v1 `# output directory`


docker run \
    --network="host" \
    --rm \
    --volume "${PWD}:/local" \
    swaggerapi/swagger-codegen-cli-v3:latest generate \
        --input-spec http://${PCAPI_HOST}/v2/deprecated/openapi.json `# schema location` \
        --additional-properties=enumPropertyNaming=original,modelPropertyNaming=original,removeEnumValuePrefix=false \
        --lang typescript-fetch `# client type` \
        --config /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        --template-dir /local/swagger_codegen/gen_templates `# templates directory` \
        --output /local/src/apiClient/v2 `# output directory`

docker run \
    --network="host" \
    --rm \
    --volume "${PWD}:/local" \
    swaggerapi/swagger-codegen-cli-v3:latest generate \
        --input-spec http://${PCAPI_HOST}/adage-iframe/openapi.json `# schema location` \
        --additional-properties=enumPropertyNaming=original,modelPropertyNaming=original,removeEnumValuePrefix=false \
        --lang typescript-fetch `# client type` \
        --config /local/swagger_codegen/swagger_codegen_config.json `# swagger codegen config` \
        --template-dir /local/swagger_codegen/gen_templates `# templates directory` \
        --output /local/src/apiClient/adage `# output directory`

success() {
  echo -e "✅  ${GREEN}$1${NO_COLOR}"
}

success "TypeScript API client and interfaces were generated successfully."
