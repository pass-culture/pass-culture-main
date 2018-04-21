// ACTIONS
export const CLOSE_VERSO = 'CLOSE_VERSO'
export const SHOW_VERSO = 'SHOW_VERSO'
export const LOCATION_CHANGE = '@@router/LOCATION_CHANGE'

// INITIAL STATE
const initialState = {
  isActive: false,
  isFlipped: false,
  unFlippable: false,
}

// REDUCER
function verso(state = initialState, action) {
  switch (action.type) {
    case CLOSE_VERSO:
      return Object.assign({}, state, { isFlipped: false })
    case SHOW_VERSO:
      return Object.assign({}, state, { isFlipped: true })
    case LOCATION_CHANGE: // Come from reservation
      if (action.payload.search.indexOf('to=verso') >= 0) {
        return Object.assign({}, state, { isFlipped: true, unFlippable: true })
      }
      return initialState
    default:
      return state
  }
}

// ACTION CREATORS
export function flip(action = {}) {
  return { type: SHOW_VERSO }
}

export function unFlip(action = {}) {
  return { type: CLOSE_VERSO }
}

// default
export default verso
