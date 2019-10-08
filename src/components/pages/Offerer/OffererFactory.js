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
  return new OffererClass(
    offerer.id,
    offerer.siren,
    offerer.name,
    offerer.address,
    offerer.bic,
    offerer.iban,
    adminUserOfferer
  )
}
