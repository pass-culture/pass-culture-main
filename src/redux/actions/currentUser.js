import { API_URL } from '../../utils/config'

export const SET_CURRENT_USER = 'SET_CURRENT_USER'

async function fetchCurrentUser() {
  const response = await fetch(`${API_URL}/users/current`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (response.status != 200) return null

  return await response.json()
}

export const setCurrentUser = value => ({ type: SET_CURRENT_USER, value })

export const resetCurrentUser = () => ({ type: SET_CURRENT_USER, value: null })

export function getCurrentUser() {
  return dispatch => {
    return fetchCurrentUser().then(currentUser => dispatch(setCurrentUser(currentUser)))
  }
}
