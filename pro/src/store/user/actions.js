export const SET_USER_IS_INITIALIZED = 'SET_USER_IS_INITIALIZED'
export const RESET_USER_IS_INITIALIZED = 'RESET_USER_IS_INITIALIZED'

export const setIsInitialized = () => ({
  type: SET_USER_IS_INITIALIZED,
})

export const resetIsInitialized = () => ({
  type: RESET_USER_IS_INITIALIZED,
})
