import { OffererClass } from './OffererClass'

export const makeOffererComponentValueObject = (
  adminUserOffererSelector,
  offererSelector,
  offererId,
  currentUserId,
  state
) => {
  const adminUserOfferer = adminUserOffererSelector(state, offererId, currentUserId, 'admin')
  const offerer = offererSelector(state, offererId)
  return new OffererClass(offerer, adminUserOfferer)
}
