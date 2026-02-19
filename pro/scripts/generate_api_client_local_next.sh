#!/usr/bin/env bash
set -e

export PCAPI_HOST=${PCAPI_HOST:-"localhost:5001"}

echo "Generating v1 (Pro) API client from http://${PCAPI_HOST}/pro/openapi.json..."
./node_modules/.bin/openapi-ts -f config/openapi-ts.v1.config.ts

echo "Generating adage API client from http://${PCAPI_HOST}/adage-iframe/openapi.json..."
./node_modules/.bin/openapi-ts -f config/openapi-ts.adage.config.ts

echo "Post-processing generated code..."

# Fix ThrowOnError default: match runtime behavior (throwOnError: true in client config)
# This makes SDK functions return Promise<T> instead of Promise<{data: T} | {error: E}>
for f in src/apiClient/v1/sdk.gen.ts src/apiClient/adage/sdk.gen.ts; do
  sed -i 's/ThrowOnError extends boolean = false/ThrowOnError extends boolean = true/g' "$f"
done

# Fix ResponseStyle default: match runtime behavior (responseStyle: 'data' in client config)
# This makes return types unwrap to just the data type instead of {data, request, response}
for f in src/apiClient/v1/client/types.gen.ts src/apiClient/adage/client/types.gen.ts; do
  sed -i "s/TResponseStyle extends ResponseStyle = 'fields'/TResponseStyle extends ResponseStyle = 'data'/g" "$f"
done

echo "Adding compatibility shims..."

# Append compat re-exports to v1/index.ts
cat >> src/apiClient/v1/index.ts << 'EOF'

// Compatibility re-exports for migration from openapi-typescript-codegen
export { ApiError, CancelablePromise, CancelError } from '../compat';
EOF

# Append compat re-exports to adage/index.ts
cat >> src/apiClient/adage/index.ts << 'EOF'

// Compatibility re-exports for migration from openapi-typescript-codegen
export { ApiError, CancelablePromise, CancelError } from '../compat';
EOF

# Create stub files at old import paths for backward compatibility
# These paths are used by tests and apiAdresse.ts

for dir in src/apiClient/v1/core src/apiClient/adage/core; do
  cat > "$dir/ApiRequestOptions.ts" << 'EOF'
// Compatibility re-export for migration from openapi-typescript-codegen
export type { ApiRequestOptions } from '../../compat';
EOF

  cat > "$dir/ApiResult.ts" << 'EOF'
// Compatibility re-export for migration from openapi-typescript-codegen
export type { ApiResult } from '../../compat';
EOF
done

echo "Done."
