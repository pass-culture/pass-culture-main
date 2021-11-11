import { TOGGLE_OVERLAY } from '../actions/overlay'

const overlay = (state = false, action) => {
  if (action.type === TOGGLE_OVERLAY) {
    return !state
  } else {
    return state
  }
}

export default overlay
