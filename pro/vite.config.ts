import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'
import tsconfigPaths from 'vite-tsconfig-paths'

const getEnvWithProcessPrefix = (mode: string): Record<string, string> => {
  const env = loadEnv(mode, process.cwd())

  // expose .env as import.meta.env instead of import.meta since jest does not import meta yet
  const envWithProcessPrefix = Object.entries(env).reduce(
    (prev, [key, val]) => ({
      ...prev,
      ['import.meta.env.' + key]: `"${val}"`,
    }),
    {}
  )
  console.log({ envWithProcessPrefix })

  return envWithProcessPrefix
}

export default defineConfig(({ mode }) => {
  // Solves issue https://github.com/vitejs/vite/issues/1973

  return {
    root: './src',
    build: {
      outDir: 'build',

      sourcemap: true,
    },
    plugins: [react(), tsconfigPaths()],
  }
})
