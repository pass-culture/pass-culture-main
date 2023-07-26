import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { createHtmlPlugin } from 'vite-plugin-html'
import tsconfigPaths from 'vite-tsconfig-paths'

// ts-unused-exports:disable-next-line
export default defineConfig(({ mode }) => {
  return {
    root: './src',
    build: {
      outDir: '../build',
      sourcemap: true,
      emptyOutDir: true,
    },
    resolve: {
      alias: { styles: 'src/styles' },
    },
    plugins: [
      react(),
      tsconfigPaths(),
      createHtmlPlugin({
        minify: true,
        entry: 'index.tsx',
        inject: { data: { mode } },
      }),
    ],
    server: { port: 3001 },
    preview: { port: 3001 },
  }
})
