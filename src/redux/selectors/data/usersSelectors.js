import { createSelector } from 'reselect'

import User from '../../../components/pages/profile/ValueObjects/User'

export const selectCurrentUser = createSelector(
  state => state.data.users,
  users => {
    if (users && users.length > 0) {
      return new User(users[0])
    }
  }
)
