// ACTIONS
export const SHOW_SPLASH = 'SHOW_SPLASH'
export const CLOSE_SPLASH = 'CLOSE_SPLASH'

// INITIAL STATE
const initialState = {
  closeTimeout: 2000,
  isActive: window.location.pathname === '/' || ['/beta'].find(pageName =>
    window.location.pathname.startsWith(pageName)),
}

// REDUCER
function splash (state = initialState, action) {
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
export function closeSplash (action = {}) {
  return { type: CLOSE_SPLASH }
}

export function showSplash (action = {}) {
  return { type: SHOW_SPLASH }
}

// default
export default splash
