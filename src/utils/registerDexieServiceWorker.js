import { IS_DEV } from './config'
import { clear, config, db, fetch, pushPull } from './dexie'
import store from './store'
import { requestData } from '../reducers/data'

const dexieSwUrl = `${process.env.PUBLIC_URL}/dexie-service-worker.js`

export function syncRedux () {
  config.collections.forEach(({ name }) =>
    name !== 'differences' && store.dispatch(
      requestData('GET', name, { sync: true })))
}

// Message Channel that triggers the sync between
// dexie push pull callback and redux update
export function sync (key, state, config = {}) {
  if (!navigator.serviceWorker.controller) {
    return
  }
  const dexieMessageChannel = new MessageChannel()
  dexieMessageChannel.port1.onmessage = event => {
    if(event.data.error) {
      console.warn(event.data.error)
    } else {
      syncRedux()
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
  window.pushPullDexie = pushPull
  window.syncDexiePushPull = () => sync('dexie-push-pull')
}
