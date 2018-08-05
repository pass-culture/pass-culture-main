import { Logger } from 'pass-culture-shared'
import {
  setGeolocationPosition,
  setGeolocationWatchId,
} from '../reducers/geolocation'

const init = store => {
  Logger.log('Geoloc queried')
  const watchId = navigator.geolocation.watchPosition(
    position => {
      Logger.log('Geoloc received', position)
      store.dispatch(setGeolocationPosition(position.coords))
    },
    err => Logger.warn('Could not get geoloc', err),
    {
      enableHighAccuracy: false,
      maximumAge: 10 * 60 * 1000, // 10 minutes
      timeout: 5 * 1000, // 5 seconds
    }
  )
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
