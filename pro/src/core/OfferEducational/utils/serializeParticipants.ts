import { IOfferEducationalFormValues } from '../types'
import { PARTICIPANTS } from '../constants'
import { StudentLevels } from 'api/v1/gen'

export const serializeParticipants = (
  participants: IOfferEducationalFormValues['participants']
): StudentLevels[] =>
  Object.keys(participants)
    .filter((key): boolean => {
      return participants[key as keyof typeof participants] === true
    })
    .map(key => PARTICIPANTS[key])
