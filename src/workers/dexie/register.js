import DexieWorker from './index.js'
import config from './config'
import { requestData } from '../../reducers/data'
import { IS_DEV } from '../../utils/config'
import store from '../../utils/store'

export const worker = new DexieWorker()

export default function register() {
  worker.onmessage = event => {
    if (event.data.error) {
      console.warn(event.data.error)
    } else {
      if (event.data.isSyncRedux) {
        syncRedux(event.data)
      }
      if (event.data.log) {
        console.log(event.data.log)
      }
    }
  }
}

export function syncRedux (payload) {
  config.collections.forEach(({ name }) => {
    const config = { local: true }
    const result = payload.results.find(result =>
      result && result.collectionName === name)
    config.deprecatedData = result && result.deprecatedData
    name !== 'differences' && store.dispatch(
      requestData('GET', name, config))
  })
}

if (IS_DEV) {
  window.dexieWorker = worker
}
