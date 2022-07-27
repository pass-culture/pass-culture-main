import { StudentLevels } from 'apiClient/v1'

import { PARTICIPANTS } from '../constants'
import { IOfferEducationalFormValues } from '../types'

export const serializeParticipants = (
  participants: IOfferEducationalFormValues['participants']
): StudentLevels[] =>
  Object.keys(participants)
    .filter((key): boolean => {
      return participants[key as keyof typeof participants] === true
    })
    .map(key => PARTICIPANTS[key])
