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
  }, (err) => {
    window.warn('Could not get geoloc', err)
  }, {
    maximumAge: 10 * 60 * 1000, // 10 minutes
    timeout: 5 * 1000, // 5 seconds
    enableHighAccuracy: false,
  })
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
