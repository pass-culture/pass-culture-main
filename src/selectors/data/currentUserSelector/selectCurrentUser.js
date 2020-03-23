import { createSelector } from 'reselect'

import currentUserUUID from './currentUserUUID'

export default createSelector(
  state => state.data.users,
  users => {
    if (!users) return
    return users.find(user => user && user.currentUserUUID === currentUserUUID)
  }
)
