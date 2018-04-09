// ACTIONS
export const SET_GEOLOCATION_POSITION = 'SET_GEOLOCATION_POSITION'
export const SET_GEOLOCATION_WATCH_ID = 'SET_GEOLOCATION_WATCH_ID'

// INITIAL STATE
const initialState = { position: null }

// REDUCER
function geolocation (state = initialState, action) {
  switch (action.type) {
    case SET_GEOLOCATION_POSITION:
      return Object.assign({}, state, { position: action.position })
    case SET_GEOLOCATION_WATCH_ID:
      return Object.assign({}, state, { watchId: action.watchId })
    default:
      return state
  }
}

// ACTION CREATORS
export function setGeolocationPosition (position) {
  return { type: SET_GEOLOCATION_POSITION, position }
}

export function setGeolocationWatchId (watchId) {
  return { type: SET_GEOLOCATION_WATCH_ID, watchId }
}

// default
export default geolocation
