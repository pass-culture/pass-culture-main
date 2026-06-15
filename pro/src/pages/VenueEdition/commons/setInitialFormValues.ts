import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import { OPENING_HOURS_DAYS } from '@/commons/utils/date'

import type { VenueEditionFormValues } from './types'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  return {
    accessibility: {
      [AccessibilityEnum.VISUAL]: venue.visualDisabilityCompliant ?? null,
      [AccessibilityEnum.MENTAL]: venue.mentalDisabilityCompliant ?? null,
      [AccessibilityEnum.AUDIO]: venue.audioDisabilityCompliant ?? null,
      [AccessibilityEnum.MOTOR]: venue.motorDisabilityCompliant ?? null,
      [AccessibilityEnum.NONE]: setAccessibilityNone(venue),
    },
    description: venue.description || '',
    email: venue.contact?.email || '',
    isAccessibilityAppliedOnAllOffers: false,
    phoneNumber: venue.contact?.phoneNumber || '',
    webSite: venue.contact?.website || '',
    isOpenToPublic: venue.isOpenToPublic.toString(),
    openingHours: normalizeOpeningHoursForForm(venue),
    activity: venue.activity as VenueEditionFormValues['activity'], // Force is needed because of "GAMES_CENTRE" which is present in `DisplayableActivity`, but not in `ActivityOpenToPublic`
    culturalDomains: venue.collectiveDomains.map((domain) => domain.name),
    volunteeringUrl: venue.volunteeringUrl ?? null,
    withdrawalDetails: venue.withdrawalDetails ?? null,
  }
}

const normalizeOpeningHoursForForm = (
  venue: GetVenueResponseModel
): VenueEditionFormValues['openingHours'] =>
  Object.fromEntries(
    OPENING_HOURS_DAYS.map((day) => [day, venue.openingHours?.[day] ?? []])
  )

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
