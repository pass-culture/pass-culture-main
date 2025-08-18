import type {
  GetVenueResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import { OPENING_HOURS_DAYS } from '@/commons/utils/date'

import type { VenueEditionFormValues } from './types'

export function getOpeningHoursFromGetVenueResponseOpeningHours(
  openingHours: GetVenueResponseModel['openingHours']
): WeekdayOpeningHoursTimespans | null {
  //  This function exists because the model for the openingHours on `getVenue`
  // is not he same as the model used elswhere for opening hours
  //  TODO : delete this function when `GetVenueResponseModel.openingHours` model is `WeekdayOpeningHoursTimespans`
  if (!openingHours) {
    return null
  }

  const formattedOpeningHours: WeekdayOpeningHoursTimespans = {}

  OPENING_HOURS_DAYS.forEach((day) => {
    if (openingHours[day] && openingHours[day].length > 0) {
      formattedOpeningHours[day] = openingHours[day].map(
        (timespan: { open: string; close: string }) => [
          timespan.open,
          timespan.close,
        ]
      )
    } else {
      formattedOpeningHours[day] = null
    }
  })

  return formattedOpeningHours
}

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  return {
    accessibility: {
      [AccessibilityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
      [AccessibilityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
      [AccessibilityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
      [AccessibilityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
      [AccessibilityEnum.NONE]: setAccessibilityNone(venue),
    },
    description: venue.description || '',
    email: venue.contact?.email || '',
    isAccessibilityAppliedOnAllOffers: false,
    phoneNumber: venue.contact?.phoneNumber || '',
    webSite: venue.contact?.website || '',
    isOpenToPublic: venue.isOpenToPublic.toString() || '',
    openingHours: getOpeningHoursFromGetVenueResponseOpeningHours(
      venue.openingHours
    ),
  }
}

function setAccessibilityNone(venue: GetVenueResponseModel): boolean {
  // for now just acceslibre
  const isSynchronized = !!venue.externalAccessibilityId

  if (isSynchronized) {
    return [
      venue.visualDisabilityCompliant,
      venue.mentalDisabilityCompliant,
      venue.audioDisabilityCompliant,
      venue.motorDisabilityCompliant,
    ].every((accessibility) => !accessibility)
  }
  return [
    venue.visualDisabilityCompliant,
    venue.mentalDisabilityCompliant,
    venue.audioDisabilityCompliant,
    venue.motorDisabilityCompliant,
  ].every((accessibility) => accessibility === false)
}
