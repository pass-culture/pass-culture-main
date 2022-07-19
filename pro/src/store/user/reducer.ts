import {
  RESET_USER_IS_INITIALIZED,
  SET_CURRENT_USER,
  SET_USER_IS_INITIALIZED,
} from './actions'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export type UserState = {
  initialized: boolean
  currentUser: null | SharedCurrentUserResponseModel
}

export const initialState: UserState = {
  initialized: false,
  currentUser: null,
}

type UserReductionAction = {
  type:
    | typeof RESET_USER_IS_INITIALIZED
    | typeof SET_CURRENT_USER
    | typeof SET_USER_IS_INITIALIZED
  currentUser: null | SharedCurrentUserResponseModel
}

export const userReducer = (
  state: UserState = initialState,
  action: UserReductionAction
) => {
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
