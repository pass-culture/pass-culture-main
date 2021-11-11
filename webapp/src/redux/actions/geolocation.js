export const SET_GEOLOCATION_POSITION = 'SET_GEOLOCATION_POSITION'
export const SET_GEOLOCATION_WATCH_ID = 'SET_GEOLOCATION_WATCH_ID'

export const setGeolocationPosition = ({ latitude, longitude }) => {
  return { latitude, longitude, type: SET_GEOLOCATION_POSITION }
}

export const setGeolocationWatchId = watchId => {
  return { type: SET_GEOLOCATION_WATCH_ID, watchId }
}
