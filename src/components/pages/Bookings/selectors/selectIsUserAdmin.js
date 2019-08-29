import { createSelector } from 'reselect'

const selectIsUserAdmin = createSelector(
  state => state.data.users,
  users => {
    if (!users || users.length < 1) {
      return false
    }
    const currentUser = users[0]
    return currentUser.isAdmin
  }
)

export default selectIsUserAdmin
