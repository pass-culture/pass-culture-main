import { StudentLevels } from '@/apiClient/v1/new'

import type { OfferEducationalFormValues } from '../types'

export const serializeParticipants = (
  participants: OfferEducationalFormValues['participants']
): StudentLevels[] =>
  Object.values(StudentLevels).filter(
    (studentLevel) => participants[studentLevel]
  )
