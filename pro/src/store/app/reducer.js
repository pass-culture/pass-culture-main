import { SET_DISPLAY_DOMAIN_BANNER, SET_LOG_EVENT } from './actions'

export const initialState = {
  displayDomainBanner: false,
  logEvent: undefined,
}

export const appReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_DISPLAY_DOMAIN_BANNER:
      return {
        ...state,
        displayDomainBanner: action.displayDomainBanner,
      }
    case SET_LOG_EVENT:
      return {
        ...state,
        logEvent: action.logEvent,
      }
    default:
      return state
  }
}
