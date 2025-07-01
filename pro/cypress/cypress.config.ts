import { defineConfig } from 'cypress'
import cypressFailFast = require('cypress-fail-fast/plugin')

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      cypressFailFast(on, config)
      // allureCypress(on, config, {
      //   resultsDir: '../../allure-results',
      // })
      // Make sure to return the config object as it might have been modified by the plugin.
      return config
    },
    baseUrl: 'http://localhost:3001',
    experimentalRunAllSpecs: true, // Run all specs test in UI mode
  },
  retries: {
    runMode: 2,
    openMode: 0,
  },
  viewportHeight: 1080,
  viewportWidth: 1920,
  defaultCommandTimeout: 30000,
  requestTimeout: 30000,
  video: false,
  watchForFileChanges: false,
  env: {
    FAIL_FAST_STRATEGY: 'run',
    FAIL_FAST_ENABLED: true,
    FAIL_FAST_BAIL: 3,
  },
})
