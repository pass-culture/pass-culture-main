import { PARTICIPANTS } from 'core/OfferEducational'

export const participantsOptions = Object.keys(PARTICIPANTS).map(key => ({
  label: PARTICIPANTS[key],
  name: `participants.${key}`,
}))
