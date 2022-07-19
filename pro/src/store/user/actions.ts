import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export const SET_USER_IS_INITIALIZED = 'SET_USER_IS_INITIALIZED'
export const RESET_USER_IS_INITIALIZED = 'RESET_USER_IS_INITIALIZED'
export const SET_CURRENT_USER = 'SET_CURRENT_USER'

export const setIsInitialized = () => ({
  type: SET_USER_IS_INITIALIZED,
})

export const resetIsInitialized = () => ({
  type: RESET_USER_IS_INITIALIZED,
})

export const setCurrentUser = (
  currentUser: SharedCurrentUserResponseModel | null
) => ({
  currentUser,
  type: SET_CURRENT_USER,
})
