import {
  setGeolocationPosition,
  setGeolocationWatchId,
} from '../reducers/geolocation'
import { worker } from '../workers/dexie/register'

const init = store => {
  window.log('queries geoloc')
  const watchId = navigator.geolocation.watchPosition(function(position) {
    store.dispatch(setGeolocationPosition(position))
    worker.postMessage({
      key: 'dexie-state',
      state: { position },
    })
  })
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
