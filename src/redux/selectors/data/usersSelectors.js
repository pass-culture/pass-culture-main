import { createSelector } from 'reselect'

export const selectCurrentUser = createSelector(
  state => state.data.users,
  users => {
    if (users && users.length > 0) {
      return users[0]
    }
  }
)
