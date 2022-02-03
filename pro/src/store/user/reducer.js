import { SET_IS_INITIALIZED } from './actions'

export const initialState = {
  initialized: false,
  currentUser: null,
}

export const userReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_IS_INITIALIZED:
      return { ...state, initialized: true }
    default:
      return state
  }
}
