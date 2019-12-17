import { createSelector } from 'reselect'
import { selectCurrentUser } from 'with-react-redux-login'

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
