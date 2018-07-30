import {
  setGeolocationPosition,
  setGeolocationWatchId,
} from '../reducers/geolocation'

const init = store => {
  window.log('Geoloc queried')
  const watchId = navigator.geolocation.watchPosition(
    position => {
      window.log('Geoloc received', position)
      store.dispatch(setGeolocationPosition(position.coords))
    },
    err => {
      window.warn('Could not get geoloc', err)
    },
    {
      maximumAge: 10 * 60 * 1000, // 10 minutes
      timeout: 5 * 1000, // 5 seconds
      enableHighAccuracy: false,
    }
  )
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
