import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig(() => {
  return {
    root: './src',
    build: {
      outDir: 'build',

      sourcemap: true,
    },
    plugins: [react(), tsconfigPaths()],
  }
})
