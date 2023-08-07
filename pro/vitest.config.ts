import { defineConfig } from 'vitest/config'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    coverage: {
      provider: 'istanbul',
      cleanOnRerun: true,
      reportsDirectory: 'src/coverage',
      reporter: ['text', 'html', 'lcov'],
    },
    reporters: 'verbose',
    setupFiles: 'src/vitest.setup.ts',
    globals: true,
    environment: 'jsdom',
    deps: { inline: ['vitest-canvas-mock'] },
    clearMocks: true,
    restoreMocks: true,
    cache: { dir: 'src/.vitest_cache' },
    css: { modules: { classNameStrategy: 'non-scoped' } },
    minThreads: 4,
    maxThreads: 6,
    testTimeout: 30000,
  },
})
