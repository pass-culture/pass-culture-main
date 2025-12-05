import type {
  EditVenueBodyModel,
  OnboardingActivity,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import type { OnboardingActivityType } from '@/commons/mappings/OnboardingActivity'
import { OPENING_HOURS_DAYS } from '@/commons/utils/date'

import { diffObjects } from '../utils/helpers'
import type { VenueEditionFormValues } from './types'

export const serializeEditVenueBodyModel = (
  formValues: VenueEditionFormValues,
  initialValues: VenueEditionFormValues,
  hideSiret: boolean,
  alreadyHasOpeningHours: boolean = false
): EditVenueBodyModel => {
  const currentPayload = buildEditVenuePayload(
    formValues,
    alreadyHasOpeningHours
  )
  const initialPayload = buildEditVenuePayload(
    initialValues,
    alreadyHasOpeningHours
  )

  // Build the final payload by diffing the current and initial payloads (PATCH payload)
  const diffPayload = diffObjects(
    currentPayload as Record<string, unknown>,
    initialPayload as Record<string, unknown>
  )

  if (hideSiret) {
    delete diffPayload.siret
  }

  return diffPayload
}

function buildEditVenuePayload(
  formValues: VenueEditionFormValues,
  alreadyHasOpeningHours: boolean
): EditVenueBodyModel {
  const normalizedActivity = normalizeActivity(formValues.activity)

  return {
    audioDisabilityCompliant: formValues.accessibility.audio,
    description: formValues.description,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    visualDisabilityCompliant: formValues.accessibility.visual,
    contact: {
      email: !formValues.email ? null : formValues.email,
      phoneNumber: !formValues.phoneNumber ? null : formValues.phoneNumber,
      website: !formValues.webSite ? null : formValues.webSite,
      socialMedias: null,
    },
    isAccessibilityAppliedOnAllOffers:
      formValues.isAccessibilityAppliedOnAllOffers,
    openingHours: serializeOpeningHours(formValues, alreadyHasOpeningHours),
    isOpenToPublic: formValues.isOpenToPublic === 'true',
    activity:
      normalizedActivity === undefined || normalizedActivity === null
        ? (normalizedActivity ?? undefined)
        : (normalizedActivity as OnboardingActivity),
  }
}

function normalizeActivity(
  activity: VenueEditionFormValues['activity']
): OnboardingActivityType | null | undefined {
  if ((activity as string | null) === 'GAMES_CENTRE') {
    return null
  }

  return activity ?? undefined
}

function serializeOpeningHours(
  formValues: VenueEditionFormValues,
  alreadyHasOpeningHours: boolean
): EditVenueBodyModel['openingHours'] {
  if (
    !alreadyHasOpeningHours &&
    !OPENING_HOURS_DAYS.some(
      (d) =>
        formValues.openingHours?.[d] && formValues.openingHours[d].length > 0
    )
  ) {
    //  If the opening hours have never been set yet, and if none of the days have a timespan set on the form,
    //  do not set the openingHours in the PATCH on the venue. Otherwise, the venue would appear "closed".
    return null
  }

  return cleanOpeningHours(formValues.openingHours)
}

export function cleanOpeningHours(
  openingHours?: WeekdayOpeningHoursTimespans | null
) {
  //  React hook form creates empty arrays for each day of the week, while the api must receive null
  //  for week days without opening hours
  const cleanedOpeningHours: WeekdayOpeningHoursTimespans = {}
  OPENING_HOURS_DAYS.forEach((day) => {
    cleanedOpeningHours[day] =
      !openingHours || !openingHours[day] || openingHours[day].length === 0
        ? null
        : openingHours[day]
  })
  return cleanedOpeningHours
}
