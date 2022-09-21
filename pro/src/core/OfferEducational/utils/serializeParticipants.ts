import { StudentLevels } from 'apiClient/v1'

import { IOfferEducationalFormValues } from '../types'

export const serializeParticipants = (
  participants: IOfferEducationalFormValues['participants']
): StudentLevels[] =>
  Object.values(StudentLevels).filter(
    studentLevel => participants[studentLevel] === true
  )
