import type {
  EditVenueBodyModel,
  OnboardingActivity,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import type { OnboardingActivityType } from '@/commons/mappings/OnboardingActivity'
import { OPENING_HOURS_DAYS } from '@/commons/utils/date'

import { diffObjects } from '../utils/helpers'
import type { VenueEditionFormValuesType } from './validationSchema'

export const serializeEditVenueBodyModel = (
  formValues: VenueEditionFormValuesType,
  initialValues: VenueEditionFormValuesType,
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
  formValues: VenueEditionFormValuesType,
  alreadyHasOpeningHours: boolean
): EditVenueBodyModel {
  const normalizedActivity = normalizeActivity(formValues.activity)

  return {
    audioDisabilityCompliant: formValues.accessibility?.audio,
    description: formValues.description,
    mentalDisabilityCompliant: formValues.accessibility?.mental,
    motorDisabilityCompliant: formValues.accessibility?.motor,
    visualDisabilityCompliant: formValues.accessibility?.visual,
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
    activity: normalizedActivity
      ? (normalizedActivity as OnboardingActivity)
      : undefined,
  }
}

function normalizeActivity(
  activity: VenueEditionFormValuesType['activity']
): OnboardingActivityType | null {
  if (activity === 'GAMES_CENTRE') {
    return null
  }

  return activity as OnboardingActivity
}

function serializeOpeningHours(
  formValues: VenueEditionFormValuesType,
  alreadyHasOpeningHours: boolean
): WeekdayOpeningHoursTimespans | null {
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
  openingHours?: VenueEditionFormValuesType['openingHours'] | null
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
