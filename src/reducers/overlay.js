const TOGGLE_OVERLAY = 'TOGGLE_OVERLAY'

// REDUCER
export const overlay = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_OVERLAY:
      return !state
    default:
      return state
  }
}

// ACTION CREATORS
export const toggleOverlay = () => ({
  type: TOGGLE_OVERLAY,
})
