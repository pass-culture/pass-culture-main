import { defineConfig, devices } from '@playwright/test'

const IS_CI = !!process.env.CI

/**
 * @see https://playwright.dev/docs/test-configuration.
 */
// eslint-disable-next-line import/no-default-export
export default defineConfig({
  testDir: './e2e',
  fullyParallel: IS_CI,
  forbidOnly: IS_CI,
  globalSetup: './playwright.globalSetup.ts',
  reporter: 'list',
  retries: IS_CI ? 2 : 0,
  workers: IS_CI ? 1 : undefined,

  use: {
    baseURL: 'http://localhost:3001',
    browserName: 'chromium',
    headless: IS_CI,
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
