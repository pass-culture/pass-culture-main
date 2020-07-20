import { createSelector } from 'reselect'

import User from '../../components/pages/profile/ValueObjects/User'

export const selectCurrentUser = createSelector(
  state => state.currentUser,
  user => user && new User(user)
)
