import { fileURLToPath, URL } from 'url'

import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, PluginOption } from 'vite'
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
      assetsInlineLimit: 0,
    },
    resolve: {
      alias: {
        styles: fileURLToPath(new URL('./src/styles', import.meta.url)),
      },
    },
    plugins: [
      react(),
      tsconfigPaths(),
      createHtmlPlugin({
        minify: true,
        inject: { data: { mode } },
      }),
      visualizer({ filename: 'bundleStats.html' }) as PluginOption,
    ],
    server: { port: 3001 },
    preview: { port: 3001 },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './vitest.setup.ts',
      clearMocks: true,
      restoreMocks: true,
      cacheDir: '../.vitest_cache',
      css: { modules: { classNameStrategy: 'non-scoped' } },
      coverage: {
        reportsDirectory: '../coverage',
        reporter: ['text', 'html', 'lcov'],
      },
      minThreads: 4,
      maxThreads: 6,
      testTimeout: 30000,
    },
    css: {
      devSourcemap: true,
    },
  }
})
