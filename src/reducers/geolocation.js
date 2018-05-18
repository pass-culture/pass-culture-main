// ACTIONS
export const SET_GEOLOCATION_POSITION = 'SET_GEOLOCATION_POSITION'
export const SET_GEOLOCATION_WATCH_ID = 'SET_GEOLOCATION_WATCH_ID'

// INITIAL STATE
const initialState = { latitude: null, longitude: null, watchId: null }

// REDUCER
function geolocation(state = initialState, action) {
  switch (action.type) {
    case SET_GEOLOCATION_POSITION:
      return Object.assign({}, state, { latitude: action.latitude || state.latitude, longitude: action.longitude || state.longitude })
    case SET_GEOLOCATION_WATCH_ID:
      return Object.assign({}, state, { watchId: action.watchId })
    default:
      return state
  }
}

// ACTION CREATORS
export function setGeolocationPosition({latitude, longitude}) {
  return { type: SET_GEOLOCATION_POSITION, latitude, longitude }
}

export function setGeolocationWatchId(watchId) {
  return { type: SET_GEOLOCATION_WATCH_ID, watchId }
}

// default
export default geolocation
