// ACTIONS
export const SHOW_SPLASH = 'SHOW_SPLASH'
export const CLOSE_SPLASH = 'CLOSE_SPLASH'

// INITIAL STATE
const initialState = {
  closeTimeout: 2000,
  isActive:
    window.location.pathname === '/' ||
    window.location.pathname.substr(0, 5) === '/beta',
}

// REDUCER
function splash(state = initialState, action) {
  switch (action.type) {
    case CLOSE_SPLASH:
      return Object.assign({}, state, { isActive: false })
    case SHOW_SPLASH:
      return Object.assign({}, state, { isActive: true })
    default:
      return state
  }
}

// ACTION CREATORS
export function closeSplash() {
  return { type: CLOSE_SPLASH }
}

export function showSplash() {
  return { type: SHOW_SPLASH }
}

// default
export default splash
