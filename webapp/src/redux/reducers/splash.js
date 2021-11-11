import { CLOSE_SPLASH, SHOW_SPLASH } from '../actions/splash'

const initialState = {
  closeTimeout: 1500,
  isActive: window.location.pathname === '/' || window.location.pathname.substr(0, 5) === '/beta',
}

const splash = (state = initialState, action) => {
  switch (action.type) {
    case CLOSE_SPLASH:
      return Object.assign({}, state, { isActive: false })
    case SHOW_SPLASH:
      return Object.assign({}, state, { isActive: true })
    default:
      return state
  }
}

export default splash
