import logger from './logger'
import { setGeolocationPosition, setGeolocationWatchId } from '../reducers/geolocation'

const initGeolocation = store => {
  logger.log('Geoloc queried')
  if (!navigator.geolocation || !navigator.geolocation.watchPosition) {
    logger.log('No Geoloc here')
    return
  }
  const watchId = navigator.geolocation.watchPosition(
    position => {
      logger.log('Geoloc received', position)
      store.dispatch(setGeolocationPosition(position.coords))
    },
    err => logger.warn('Could not get geoloc', err),
    {
      enableHighAccuracy: false,
      maximumAge: 10 * 60 * 1000, // 10 minutes
      timeout: 5 * 1000, // 5 seconds
    }
  )
  store.dispatch(setGeolocationWatchId(watchId))
}

export default initGeolocation
