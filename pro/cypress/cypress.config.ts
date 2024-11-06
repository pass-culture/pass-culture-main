import { defineConfig } from 'cypress'
import cypressFailFast = require('cypress-fail-fast/plugin')
import fs from 'fs'

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      cypressFailFast(on, config)
      on(
        'after:spec',
        (spec: Cypress.Spec, results: CypressCommandLine.RunResult) => {
          if (results && results.video) {
            // Do we have failures for any retry attempts?
            const failures = results.tests.some((test) =>
              test.attempts.some((attempt) => attempt.state === 'failed')
            )
            if (!failures) {
              // delete the video if the spec passed and no tests retried
              fs.unlinkSync(results.video)
            }
          }
        }
      )
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
  video: true,
  videoCompression: true,
  watchForFileChanges: false,
  env: {
    FAIL_FAST_STRATEGY: 'run',
    FAIL_FAST_ENABLED: true,
    FAIL_FAST_BAIL: 3,
  },
})
