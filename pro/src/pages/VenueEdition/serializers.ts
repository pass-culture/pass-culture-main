import type { EditVenueBodyModel } from '@/apiClient/v1'
import { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { OPENING_HOURS_DAYS } from '@/commons/utils/date'

import type { VenueEditionFormValues } from './types'

export const serializeEditVenueBodyModel = (
  formValues: VenueEditionFormValues,
  hideSiret: boolean,
  alreadyHasOpeningHours: boolean = false
): EditVenueBodyModel => {
  const payload: EditVenueBodyModel = {
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
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}

function serializeOpeningHours(
  formValues: VenueEditionFormValues,
  alreadyHasOpeningHours: boolean
): EditVenueBodyModel['openingHours'] {
  if (
    !alreadyHasOpeningHours &&
    !OPENING_HOURS_DAYS.some(
      (d) =>
        formValues.openingHours &&
        formValues.openingHours[d] &&
        formValues.openingHours[d].length > 0
    )
  ) {
    //  If the opening hours have never been set yet, and if none of the days have a timespan set on the form,
    //  do not set the openingHours in the PATCH on the venue. Otherwise, the venue would appear "closed".
    return null
  }

  const openingHours: WeekdayOpeningHoursTimespans = {}
  OPENING_HOURS_DAYS.forEach((day) => {
    openingHours[day] =
      !formValues.openingHours ||
      !formValues.openingHours[day] ||
      formValues.openingHours[day].length === 0
        ? null
        : formValues.openingHours[day]
  })
  return openingHours
}
