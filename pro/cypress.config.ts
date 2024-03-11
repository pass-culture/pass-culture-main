import { defineConfig } from 'cypress'

const API_BASE_URL = 'http://localhost:5001' || process.env.API_BASE_URL

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    setupNodeEvents(on) {
      // implement node event listeners here
      on('before:run', async () => {
        // eslint disable-next-line no-console
        console.log('before:run ~~~ ~~~ ~~~ ~~~ ~~~ end')
        try {
          await fetch(`${API_BASE_URL}/health/api`)
          console.log('health check success')
        } catch (error) {
          console.error(error)
          throw error
        }
        try {
          await fetch(`${API_BASE_URL}/e2e/pro/tear-up`)
            .then((res) => res.status)
            .then(console.log)
        } catch (error) {
          console.error(error)
          throw error
        }
      })
      on('after:run', async (results: any) => {
        /* ... */
        console.log('after:run ~~~ ~~~ ~~~ ~~~ ~~~')
        console.log(results)
        console.log('after:run ~~~ ~~~ ~~~ ~~~ ~~~ end')

        try {
          await fetch(`${API_BASE_URL}/e2e/pro/tear-down`)
          .then(res => res.status)
          .then(console.log)
        } catch (error) {
          console.error(error)
          throw error
        }
      })
    },
    baseUrl: 'http://localhost:3001',
    experimentalRunAllSpecs: true, // Run all specs test in UI mode
  },
  retries: {
    runMode: 2,
    openMode: 0,
  },
  defaultCommandTimeout: 30000,
  requestTimeout: 30000,
  viewportHeight: 1080,
  viewportWidth: 1920,
  video: true,
  videoCompression: true,
})
