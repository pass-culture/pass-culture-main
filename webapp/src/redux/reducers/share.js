import { TOGGLE_SHARE_POPIN } from '../actions/share'

const initialState = { options: null, visible: false }

const share = (state = initialState, action) => {
  if (action.type === TOGGLE_SHARE_POPIN) {
    return { options: action.options, visible: Boolean(action.options) }
  } else {
    return state
  }
}

export default share
