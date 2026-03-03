import { fileURLToPath, URL } from 'node:url'
import { fontPreloads } from '@pass-culture/design-system/lib/global/font-preloads'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, type PluginOption } from 'vite'
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
      visualizer({ filename: 'bundleStats.html' }) as PluginOption,
      htmlPlugin(mode),
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

const CSP_DEV =
  "default-src 'self' 'unsafe-eval' blob: data: https: http: gap://ready https://*.hotjar.com:* https://*.hotjar.io wss://*.hotjar.com https://*.getbeamer.com/; connect-src 'self' data: https: http: ws://*:3001 wss://*:3001; style-src 'self' https://app.getbeamer.com/styles/beamer-embed.css https://app.getbeamer.com/styles/beamer-embed-fonts.css https://app.getbeamer.com/styles/beamer-boosted-embed.css https://fonts.googleapis.com/css https://cdn.jsdelivr.net/npm/orejime@3.1.0/dist/orejime-standard.css 'unsafe-inline'"

const CSP_PROD =
  "default-src 'self' blob: data: https: http: gap://ready https://*.hotjar.com:* https://*.hotjar.io wss://*.hotjar.com https://*.getbeamer.com/; style-src 'self' https://app.getbeamer.com/styles/beamer-embed.css https://app.getbeamer.com/styles/beamer-embed-fonts.css https://app.getbeamer.com/styles/beamer-boosted-embed.css https://fonts.googleapis.com/css https://cdn.jsdelivr.net/npm/orejime@3.1.0/dist/orejime-standard.css 'unsafe-inline'"

const htmlPlugin = (mode: string) => {
  return {
    name: 'html-transform',
    transformIndexHtml(html: string) {
      const csp = mode === 'development' ? CSP_DEV : CSP_PROD
      /*
       * Do not use hashes to define CSP: we had a bug where Beamer was not loaded
       * because the hash was invalid in some instances of Firefox.
       * It is probably a Firefox bug where the hash is not computed correctly/is not reliable.
       */
      const cspTag = `<meta http-equiv="Content-Security-Policy" content="${csp}" />`

      return html
        .replace('<!-- inject:csp -->', cspTag)
        .replace(
          /<!-- inject:preload-design-system-fonts --><!-- endinject -->/g,
          fontPreloads
        )
    },
  }
}
