import { IS_DEV } from './config'
import { clear, config, db, fetch, pull } from './dexie'
import store from './store'
import { requestData } from '../reducers/data'

const dexieSwUrl = `${process.env.PUBLIC_URL}/dexie-service-worker.js`

// Message Channel that triggers the sync between
// dexie pull callback and redux update
export function sync (key, state) {
  if (!navigator.serviceWorker.controller) {
    return
  }
  const dexieMessageChannel = new MessageChannel()
  dexieMessageChannel.port1.onmessage = event => {
    if(event.data.error) {
      console.warn(event.data.error)
    } else {
      config.collections.forEach(({ name }) =>
        store.dispatch(requestData('GET', name, { sync: true })))
    }
  }
  return navigator.serviceWorker.controller.postMessage(
    { key, state, type: 'sync' },
    [dexieMessageChannel.port2]
  )
}

export default async function registerDexieServiceWorker() {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register(dexieSwUrl)
    if (!navigator.serviceWorker.ready) {
      return
    }
    sync("dexie-init")
    return registration
  }
}

if (IS_DEV) {
  window.clearDexie = clear
  window.dexieDb = db
  window.fetchDexie = fetch
  window.pullDexie = pull
  window.syncDexiePull = () => sync('dexie-pull')
}
