import { RESET_USER_IS_INITIALIZED, SET_USER_IS_INITIALIZED } from './actions'

export const initialState = {
  initialized: false,
  currentUser: null,
}

export const userReducer = (state = initialState, action) => {
  switch (action.type) {
    case RESET_USER_IS_INITIALIZED:
      return { ...state, initialized: false }
    case SET_USER_IS_INITIALIZED:
      return { ...state, initialized: true }
    default:
      return state
  }
}
