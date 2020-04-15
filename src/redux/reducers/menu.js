import { TOGGLE_MAIN_MENU } from '../actions/menu'

const menu = (state = false, action) => {
  if (action.type === TOGGLE_MAIN_MENU) {
    return !state
  } else {
    return state
  }
}

export default menu
