import { createSelector } from 'reselect'
import { selectCurrentUser } from './data/usersSelectors'

const selectIsUserAdmin = createSelector(
  selectCurrentUser,
  currentUser => {
    if (!currentUser) {
      return false
    }
    return currentUser.isAdmin
  }
)

export default selectIsUserAdmin
