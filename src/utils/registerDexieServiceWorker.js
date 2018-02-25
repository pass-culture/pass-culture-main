import { IS_DEV } from './config'
import { clear, db, fetch, pull } from './dexie'

const dexieSwUrl = `${process.env.PUBLIC_URL}/dexie-service-worker.js`

export default async function registerDexieServiceWorker() {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register(dexieSwUrl)
    if (!navigator.serviceWorker.ready) {
      return
    }
    registration.sync.register('dexie-pull')
    return registration
  }
}

if (IS_DEV) {
  window.clearDexie = clear
  window.dexieDb = db
  window.fetchDexie = fetch
  window.pullDexie = pull
}
