import { createSelector } from 'reselect'

export const selectCurrentUser = createSelector(
  state => state.data.users,
  users => {
    if (!users) return
    return users[0]
  }
)

export const resolveCurrentUser = userFromRequest => {
  if (!userFromRequest) {
    return null
  }
  return userFromRequest
}
