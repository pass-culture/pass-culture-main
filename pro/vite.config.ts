import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import tsconfigPaths from 'vite-tsconfig-paths'

// ts-unused-exports:disable-next-line
export default defineConfig(() => {
  return {
    root: './src',
    build: {
      outDir: 'build',
      sourcemap: true,
    },
    resolve: {
      alias: {
        styles: 'src/styles',
      },
    },
    plugins: [react(), tsconfigPaths()],
  }
})
