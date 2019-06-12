import { createSelector } from 'reselect'
import uuid from 'uuid'

export const selectCurrentUser = createSelector(
  state => state.data.users,
  users =>
    users.find(
      user => user && user.currentUserUUID === selectCurrentUser.currentUserUUID
    )
)

export function resolveCurrentUser(userFromRequest) {
  if (!userFromRequest) {
    return null
  }

  // give to this user an id that will make
  // selectCurrentUser the only selector able to refind it
  const currentUserUUID = uuid()
  selectCurrentUser.currentUserUUID = currentUserUUID

  return Object.assign({ currentUserUUID }, userFromRequest)
}

export default selectCurrentUser
