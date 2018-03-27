// ACTIONS
export const SHOW_NAVIGATION = 'SHOW_NAVIGATION'
export const CLOSE_NAVIGATION = 'CLOSE_NAVIGATION'
export const SHOW_VERSO = 'SHOW_VERSO'
export const HIDE_VERSO = 'HIDE_VERSO'

// INITIAL STATE
const initialState = {
  isActive: false,
  isFlipped: false,
}

// REDUCER
function navigation (state = initialState, action) {
  switch (action.type) {
    case SHOW_NAVIGATION:
      return Object.assign({}, state, { isActive: true })
    case CLOSE_NAVIGATION:
      return Object.assign({}, state, { isActive: false })
    case SHOW_VERSO:
      return Object.assign({}, state, { isFlipped: true })
    case HIDE_VERSO:
      return Object.assign({}, state, { isFlipped: false })
    default:
      return state
  }
}

// ACTION CREATORS
export function closeNavigation (action = {}) {
  return { type: CLOSE_NAVIGATION }
}

export function showNavigation (action = {}) {
  return { type: SHOW_NAVIGATION }
}

// ACTION CREATORS
export function flip (action = {}) {
  return { type: SHOW_VERSO }
}

export function unFlip (action = {}) {
  return { type: HIDE_VERSO }
}

// default
export default navigation
