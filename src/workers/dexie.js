import { requestData } from '../reducers/data'
import { IS_DEV } from '../utils/config'
import { config } from '../utils/dexie.data'
import store from '../utils/store'

// console.log('process.env.HAS_WORKERS', process.env.HAS_WORKERS)
let DexieWorker
if (process.env.HAS_WORKERS) {
  DexieWorker = require('../index.dexie.worker.js')
} else {
  DexieWorker = require('../utils/dexie.wrapper').default
}

export const worker = new DexieWorker()

export default function register() {
  worker.onmessage = event => {
    if (event.data.error) {
      console.warn(event.data.error)
    } else {
      if (event.data.isSyncRedux) {
        syncRedux()
      }
      if (event.data.log) {
        console.log(event.data.log)
      }
    }
  }
}

export function syncRedux () {
  config.collections.forEach(({ name }) =>
    name !== 'differences' && store.dispatch(
      requestData('GET', name, { sync: true })))
}

// if (IS_DEV) {
  window.dexieWorker = worker
// }
