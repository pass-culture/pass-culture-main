// ACTIONS
export const SET_GEOLOCATION_POSITION = 'SET_GEOLOCATION_POSITION'

// INITIAL STATE
const initialState = { position: null }

// REDUCER
function geolocation (state = initialState, action) {
  switch (action.type) {
    case SET_GEOLOCATION_POSITION:
      return Object.assign({}, state, { position: action.position })
    default:
      return state
  }
}

// ACTION CREATORS
export function setGeolocationPosition (position) {
  return { type: SET_GEOLOCATION_POSITION, position }
}

// default
export default geolocation
