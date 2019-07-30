import logger from './logger'
import { setGeolocationPosition, setGeolocationWatchId } from '../reducers/geolocation'

const initGeolocation = store => {
  if (!navigator.geolocation || !navigator.geolocation.watchPosition) {
    return
  }

  const tenMinutes = 10 * 60 * 1000
  const oneMinute = 1 * 60 * 1000
  const watchId = navigator.geolocation.watchPosition(
    position => {
      store.dispatch(setGeolocationPosition(position.coords))
    },
    err => logger.warn('Could not get geoloc', err),
    {
      enableHighAccuracy: false,
      maximumAge: tenMinutes,
      timeout: oneMinute,
    }
  )

  store.dispatch(setGeolocationWatchId(watchId))
}

export default initGeolocation
