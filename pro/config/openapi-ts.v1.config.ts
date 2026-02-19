import { defineConfig } from '@hey-api/openapi-ts'

const PCAPI_HOST = process.env.PCAPI_HOST ?? 'localhost:5001'

function camelCaseFromOperationId(operation: {
  operationId?: string
  method: string
}) {
  const id = operation.operationId
  if (!id) {
    return [operation.method.toLowerCase()]
  }
  return [id.charAt(0).toLowerCase() + id.slice(1)]
}

export default defineConfig({
  input: `http://${PCAPI_HOST}/pro/openapi.json`,
  output: {
    path: 'src/apiClient/v1',
    clean: true,
    postProcess: ['biome:format'],
  },
  plugins: [
    {
      name: '@hey-api/typescript',
      enums: 'typescript',
      case: 'preserve',
    },
    {
      name: '@hey-api/sdk',
      operations: {
        nesting: camelCaseFromOperationId,
      },
    },
    {
      name: '@hey-api/client-fetch',
      runtimeConfigPath: '../clientConfig',
    },
  ],
})
