// ACTIONS
export const CLOSE_VERSO = 'CLOSE_VERSO'
export const SHOW_VERSO = 'SHOW_VERSO'
export const MAKE_UNDRAGGABLE = 'MAKE_UNDRAGGABLE'
export const MAKE_DRAGGABLE = 'MAKE_DRAGGABLE'
export const LOCATION_CHANGE = '@@router/LOCATION_CHANGE'

// INITIAL STATE
const initialState = {
  isActive: false,
  isFlipped: false,
  unFlippable: false,
  draggable: true,
}

// REDUCER
function verso(state = initialState, action) {
  switch (action.type) {
    case CLOSE_VERSO:
      return Object.assign({}, state, { isFlipped: false })
    case SHOW_VERSO:
      return Object.assign({}, state, { isFlipped: true })
    case MAKE_UNDRAGGABLE:
      return Object.assign({}, state, { draggable: false})
    case MAKE_DRAGGABLE:
      return Object.assign({}, state, { draggable: true})
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

export function makeUndraggable(action = {}) {
  return { type: MAKE_UNDRAGGABLE}
}

export function makeDraggable(action = {}) {
  return { type: MAKE_DRAGGABLE}
}

// default
export default verso
