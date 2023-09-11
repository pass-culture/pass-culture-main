import { defineConfig } from 'cypress'

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    setupNodeEvents() {
      // implement node event listeners here
    },
  },
  retries: {
    runMode: 2,
    openMode: 0,
  },
  defaultCommandTimeout: 30000,
  viewportHeight: 1080,
  viewportWidth: 1920,
  video: true,
  videoCompression: true,
})
