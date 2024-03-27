import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'

import { VenueEditionFormValues } from './types'

export const buildAccessibilityFormValues = (
  venue: GetVenueResponseModel | VenueListItemResponseModel
) => {
  return {
    [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
    [AccessiblityEnum.NONE]: [
      venue.visualDisabilityCompliant,
      venue.mentalDisabilityCompliant,
      venue.audioDisabilityCompliant,
      venue.motorDisabilityCompliant,
    ].every((accessibility) => accessibility === false),
  }
}

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  return {
    accessibility: buildAccessibilityFormValues(venue),
    description: venue.description || '',
    email: venue.contact?.email || '',
    isAccessibilityAppliedOnAllOffers: false,
    phoneNumber: venue.contact?.phoneNumber || '',
    webSite: venue.contact?.website || '',
    days: [],
    monday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    tuesday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    wednesday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    thursday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    friday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    saturday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
    sunday: {
      morningStartingHour: '',
      morningEndingHour: '',
      afternoonStartingHour: '',
      afternoonEndingHour: '',
    },
  }
}
