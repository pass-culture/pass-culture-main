import { createSelector } from 'reselect'

export const selectCurrentUser = createSelector(
  state => state.data.users,
  users => {
    if (users && users.length > 0) {
      return users[0]
    }
  }
)

export const resolveCurrentUser = userFromRequest => {
  if (!userFromRequest) {
    return null
  }
  return userFromRequest
}

export const selectIsUserAdmin = createSelector(selectCurrentUser, currentUser => {
  if (!currentUser) {
    return false
  }
  return currentUser.isAdmin
})

// Do not use reselect cause they aren't refresh in test when we change initial state.
export const hasSeenTutorial = state => {
  const currentUser = state.data.users && state.data.users.length ? state.data.users[0] : null
  return currentUser?.hasSeenProTutorials || false
}
