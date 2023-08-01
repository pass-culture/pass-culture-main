import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig } from 'vite'
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
      createHtmlPlugin({
        minify: true,
        inject: { data: { mode } },
      }),
      visualizer({ filename: 'bundleStats.html' }),
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
      coverage: {
        reportsDirectory: '../coverage',
        reporter: ['text', 'html', 'lcov'],
      },
      minThreads: 4,
      maxThreads: 6,
      testTimeout: 30000,
    },
  }
})
