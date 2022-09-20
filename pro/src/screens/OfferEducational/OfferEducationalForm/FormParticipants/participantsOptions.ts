import { PARTICIPANTS } from 'core/OfferEducational'

export const participantsOptions = [
  { label: 'Tout sélectionner', name: 'participants.all' },
  ...Object.keys(PARTICIPANTS).map(key => ({
    label: PARTICIPANTS[key],
    name: `participants.${key}`,
  })),
]
