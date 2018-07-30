import { requestData } from 'pass-culture-shared'

import DexieWorker from './index.js'
import config from './config'
// import { showEstimatedQuota } from './storage'
import { IS_DEV } from '../../utils/config'

export const worker = new DexieWorker()

export default function register(store) {
  worker.onmessage = event => {
    if (event.data.error) {
      console.warn(event.data.error)
    } else {
      if (event.data.isSyncRedux) {
        syncRedux(store, event.data)
      }
      if (event.data.log) {
        console.log(event.data.log)
      }
    }
  }
  // check if quota is okay
  if (IS_DEV) {
    // showEstimatedQuota().then(quota => console.log('quota', quota))
  }
}

export function syncRedux(store, payload) {
  config.collections.forEach(({ key, name }) => {
    const config = { key, local: true }
    const result = (payload.results || []).find(
      result => result && result.collectionName === name
    )
    config.deprecatedData = result && result.deprecatedData
    name !== 'differences' && store.dispatch(requestData('GET', name, config))
  })
}

if (IS_DEV) {
  window.dexieWorker = worker
}
