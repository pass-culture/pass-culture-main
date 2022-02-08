import { SET_DISPLAY_DOMAIN_BANNER } from './actions'

export const initialState = {
  displayDomainBanner: false,
}

export const appReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_DISPLAY_DOMAIN_BANNER:
      return {
        ...state,
        displayDomainBanner: action.displayDomainBanner,
      }
    default:
      return state
  }
}
