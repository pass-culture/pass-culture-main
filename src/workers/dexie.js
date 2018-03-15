import DexieWorker from '../index.dexie.worker.js'
import { requestData } from '../reducers/data'
import { IS_DEV } from '../utils/config'
import { clear, config, db, fetch, pushPull } from '../utils/dexie'
import store from '../utils/store'

export const worker = new DexieWorker()

export default function register() {
  worker.onmessage = event => {
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
    worker.postMessage({ key: 'dexie-push-pull' })
}
