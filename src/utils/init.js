import { setGeolocationPosition,
  setGeolocationWatchId } from '../reducers/geolocation'

const init = store => {
  const watchId = navigator.geolocation.watchPosition(function(position) {
    store.dispatch(setGeolocationPosition(position))
  });
  store.dispatch(setGeolocationWatchId(watchId))
}

export default init
