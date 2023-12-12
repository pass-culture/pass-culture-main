import { defineConfig } from 'cypress'

/**
 * ceci est un poc rapide des besoins coté e2e front (pas testé)
 * ensuite il faut:
 * 
 * 1. Créér les endpoints tear-up et tear-down avec création de data (et possibilité de rerun N fois sans risque de duplicate)
 *   - s'assurer que ces endpoints soit installés uniquement sur des api spawner (donc pas testing/staging/integration/production)
 * 2. Supprimer le data set des test e2e dans la sandbox
 * 3. Typer le code JS ici :)
 */
const API_BASE_URL = 'http://localhost:50001' || process.env.API_BASE_URL

// ts-unused-exports:disable-next-line
export default defineConfig({
  e2e: {
    setupNodeEvents(on: any) {
      // implement node event listeners here
      on('before:run', async (results: any) => {
        /* ... */
        console.log('before:run ~~~ ~~~ ~~~ ~~~ ~~~')
        console.log(results)
        console.log('before:run ~~~ ~~~ ~~~ ~~~ ~~~ end')
        try {
          const response = await fetch(`${API_BASE_URL}/e2e/pro/tear-up`)  
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
          const response = await fetch(`${API_BASE_URL}/e2e/pro/tear-down`)  
        } catch (error) {
          console.error(error)
          throw error
        }
      })
    },
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
