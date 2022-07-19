import {
  RESET_USER_IS_INITIALIZED,
  SET_CURRENT_USER,
  SET_USER_IS_INITIALIZED,
} from './actions'

export const initialState = {
  initialized: false,
  currentUser: null,
}

export const userReducer = (state = initialState, action) => {
  switch (action.type) {
    case RESET_USER_IS_INITIALIZED:
      return { ...state, initialized: false, currentUser: null }
    case SET_USER_IS_INITIALIZED:
      return { ...state, initialized: true }
    case SET_CURRENT_USER:
      return { ...state, currentUser: action.currentUser }
    default:
      return state
  }
}
