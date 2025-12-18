import { defineConfig, devices } from '@playwright/test'

const BASE_URL = process.env.BASE_URL ?? 'http://localhost:3001'

export default defineConfig({
  expect: {
    timeout: 10000,
  },
  forbidOnly: !!process.env.CI,
  fullyParallel: false,
  maxFailures: 0,
  reporter: process.env.CI ? 'html' : 'list',
  testDir: '../e2e',
  testMatch: '**/*.e2e.ts',
  timeout: 60000,
  workers: 1,

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
      testIgnore: /.*\.setup\.ts/,
    },
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
      dependencies: ['chromium'],
      testIgnore: /.*\.setup\.ts/,
    },
  ],

  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },
})
