import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import environment from 'vite-plugin-environment'
import { createHtmlPlugin } from 'vite-plugin-html'
import tsconfigPaths from 'vite-tsconfig-paths'

// ts-unused-exports:disable-next-line
export default defineConfig(({ mode }) => {
  return {
    root: './src',
    build: {
      outDir: '../build',
      sourcemap: false,
      emptyOutDir: true,
    },
    resolve: {
      alias: { styles: 'src/styles' },
    },
    plugins: [
      react(),
      tsconfigPaths(),
      // Temporary plugin to expose env variables in the `process.env` object
      // Once we move to Vitest we should remove this plugin and use the
      // `import.meta.env` object instead
      environment('all', { prefix: 'VITE_' }),
      createHtmlPlugin({
        minify: true,
        inject: { data: { mode } },
      }),
    ],
    server: { port: 3001 },
    preview: { port: 3001 },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './vitest.setup.ts',
      deps: { inline: ['vitest-canvas-mock'] },
      clearMocks: true,
      restoreMocks: true,
      cache: { dir: '../.vitest_cache' },
      css: { modules: { classNameStrategy: 'non-scoped' } },
      coverage: { reportsDirectory: '../coverage' },
      minThreads: 6,
      maxThreads: 6,
      testTimeout: 10000,
    },
  }
})
