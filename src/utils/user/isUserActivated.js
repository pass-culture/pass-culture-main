import isUserValid from './isUserValid'

export const isUserActivated = user =>
  (isUserValid(user) && Boolean(user.wallet_is_activated)) || false

export default isUserActivated
