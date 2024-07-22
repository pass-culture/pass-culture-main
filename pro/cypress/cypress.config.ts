import { addCucumberPreprocessorPlugin } from '@badeball/cypress-cucumber-preprocessor'
import { createEsbuildPlugin } from '@badeball/cypress-cucumber-preprocessor/esbuild'
import createBundler from '@bahmutov/cypress-esbuild-preprocessor'
import { defineConfig } from 'cypress'

async function setupNodeEvents(
  on: Cypress.PluginEvents,
  config: Cypress.PluginConfigOptions
): Promise<Cypress.PluginConfigOptions> {
  // This is required for the preprocessor to be able to generate JSON reports after each run, and more,
  await addCucumberPreprocessorPlugin(on, config)

  on(
    'file:preprocessor',
    createBundler({
      plugins: [createEsbuildPlugin(config)],
    })
  )

  // Make sure to return the config object as it might have been modified by the plugin.
  return config
}

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    specPattern: '**/*.feature',

    setupNodeEvents,

    baseUrl: 'http://localhost:3001',
    experimentalRunAllSpecs: true, // Run all specs test in UI mode
  },
  retries: {
    runMode: 2,
    openMode: 0,
  },
  viewportHeight: 1080,
  viewportWidth: 1920,
  video: true,
  videoCompression: true,
  watchForFileChanges: false,
})
