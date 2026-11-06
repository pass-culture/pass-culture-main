import { defineConfig } from '@hey-api/openapi-ts'

const PCAPI_HOST = process.env.PCAPI_HOST ?? 'localhost:5001'

export default defineConfig({
  input: `http://${PCAPI_HOST}/pro/openapi.json`,
  output: {
    path: 'src/apiClient/zod/',
    clean: true,
  },
  plugins: ['zod'],
})
