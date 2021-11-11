import { getCurrentUser, patchCurrentUser } from './repository/currentUser'

export const SET_CURRENT_USER = 'SET_CURRENT_USER'

export const setCurrentUser = value => ({ type: SET_CURRENT_USER, value })

export const resetCurrentUser = () => ({ type: SET_CURRENT_USER, value: null })

export function fetchCurrentUser() {
  return async dispatch => {
    const currentUser = await getCurrentUser()
    return dispatch(setCurrentUser(currentUser))
  }
}

export function updateCurrentUser(payload) {
  return async dispatch => {
    const currentUser = await patchCurrentUser(payload)
    return dispatch(setCurrentUser(currentUser))
  }
}
