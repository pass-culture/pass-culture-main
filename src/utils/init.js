import {
  setGeolocationPosition,
  setGeolocationWatchId,
} from '../reducers/geolocation'
import { worker } from '../workers/dexie/register'

const init = store => {
  window.log('Geoloc queried')
  const watchId = navigator.geolocation.watchPosition((position) => {
    window.log('Geoloc received', position)
    store.dispatch(setGeolocationPosition(position))
    worker.postMessage({
      key: 'dexie-state',
      state: { position },
    })
  })
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
