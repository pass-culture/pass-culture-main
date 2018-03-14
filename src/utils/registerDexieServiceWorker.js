import { IS_DEV } from './config'
import { clear, config, db, fetch, pushPull } from './dexie'
import store from './store'
import Worker from '../dexie.service.worker.js'
import { requestData } from '../reducers/data'

export const dexieWorker = new Worker()

export default function register() {
  dexieWorker.onmessage = event => {
    if (event.data.error) {
      console.warn(event.data.error)
    } else if (event.data.isSyncRedux) {
      syncRedux()
    }
  }
}

export function syncRedux () {
  config.collections.forEach(({ name }) =>
    name !== 'differences' && store.dispatch(
      requestData('GET', name, { sync: true })))
}

if (IS_DEV) {
  window.clearDexie = clear
  window.dexieDb = db
  window.fetchDexie = fetch
  window.pushPullDexie = pushPull
  window.syncDexiePushPull = () =>
    dexieWorker.postMessage({ key: 'dexie-push-pull' })
}
