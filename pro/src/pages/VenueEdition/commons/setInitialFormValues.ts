import type { GetVenueResponseModel } from '@/apiClient/v1'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import type { DisplayedActivityType } from '@/commons/mappings/DisplayedActivity'

import type { VenueEditionFormValuesType } from './validationSchema'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValuesType => {
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
    openingHours: venue.openingHours ?? null,
    activity: venue.activity as DisplayedActivityType, // Force is needed because of "GAMES_CENTRE" which is present in `DisplayedActivity`, but not in `OnboardingActivity`
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
