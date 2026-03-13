import { defineConfig } from '@hey-api/openapi-ts'

import { stringResolverWithErrorMessages } from './src/apiClient/resolvers/stringResolver'

// biome-ignore lint/style/noDefaultExport: This is a config file.
export default defineConfig({
  input: 'http://localhost:5001/pro/openapi.json',
  output: 'src/apiClient/hey-api',
  plugins: [
    '@hey-api/typescript',
    {
      name: 'zod',
      '~resolvers': {
        // @ts-expect-error
        string: stringResolverWithErrorMessages,
      },
    },
  ],
})
