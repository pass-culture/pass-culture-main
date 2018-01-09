// ACTIONS
export const SHOW_NAVIGATION = 'SHOW_NAVIGATION'
export const CLOSE_NAVIGATION = 'CLOSE_NAVIGATION'

// INITIAL STATE
const initialState = { isActive: false }

// REDUCER
function navigation (state = initialState, action) {
  switch (action.type) {
    case SHOW_NAVIGATION:
      return Object.assign({}, state, { isActive: true })
    case CLOSE_NAVIGATION:
      return Object.assign({}, state, { isActive: false })
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

// default
export default navigation
