import { SET_GEOLOCATION_POSITION, SET_GEOLOCATION_WATCH_ID } from '../actions/geolocation'

const initialState = { latitude: null, longitude: null, watchId: null }

const geolocation = (state = initialState, action) => {
  switch (action.type) {
    case SET_GEOLOCATION_POSITION:
      return Object.assign({}, state, {
        latitude: action.latitude || state.latitude,
        longitude: action.longitude || state.longitude,
      })
    case SET_GEOLOCATION_WATCH_ID:
      return Object.assign({}, state, { watchId: action.watchId })
    default:
      return state
  }
}

export default geolocation
