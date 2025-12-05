import { fileURLToPath, URL } from 'node:url'
import { fontPreloads } from '@pass-culture/design-system/lib/global/font-preloads'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, type PluginOption } from 'vite'
import { createHtmlPlugin } from 'vite-plugin-html'
import tsconfigPaths from 'vite-tsconfig-paths'
import { configDefaults, coverageConfigDefaults } from 'vitest/config'

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
      htmlPlugin(),
    ],
    server: { port: 3001 },
    preview: { port: 3001 },
    test: {
      root: '.',
      globals: true,
      environment: 'jsdom',
      setupFiles: [
        './src/vitest.polyfills.ts',
        'allure-vitest/setup',
        './src/vitest.setup.ts',
      ],
      reporters: process.env.GITHUB_ACTIONS
        ? ['verbose', 'github-actions']
        : ['verbose'],
      clearMocks: true,
      restoreMocks: true,
      cacheDir: '.vitest_cache',
      css: { modules: { classNameStrategy: 'non-scoped' } },
      coverage: {
        provider: 'istanbul',
        reportsDirectory: 'coverage',
        reporter: ['text', 'json'],
        exclude: [
          '**/__mocks__/*',
          '**/factories/*',
          '**/tests/*',
          '**/*.stories.tsx',
          'config/*',
          'e2e/*',
          'scripts/*',
          'src/apiClient/adage/*',
          'src/apiClient/adresse/*',
          'src/apiClient/v1/*',
          'src/vitest.*.ts',
          'docs-build/**',
          'storybook-static/**',
          ...coverageConfigDefaults.exclude,
        ],
      },
      minThreads: 4,
      maxThreads: 6,
      testTimeout: 30000,
      exclude: ['**/*.stories.tsx', ...configDefaults.exclude],
      env: {
        TZ: 'UTC',
      },
    },
    css: {
      devSourcemap: true,
      preprocessorOptions: {
        scss: {
          api: 'modern',
        },
      },
    },
  }
})

const htmlPlugin = () => {
  //  Inject the design-system fonts files in the index.html preloads
  return {
    name: 'html-transform',
    transformIndexHtml(html: string) {
      return html.replace(
        /<!-- inject:preload-design-system-fonts --><!-- endinject -->/g,
        fontPreloads
      )
    },
  }
}
