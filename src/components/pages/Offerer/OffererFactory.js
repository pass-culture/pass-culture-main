import get from 'lodash.get'
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
  const offererName = get(state, 'form.offerer.name')
  return new OffererClass(offerer.id, offererName, offerer.bic, offerer.iban, adminUserOfferer)
}
