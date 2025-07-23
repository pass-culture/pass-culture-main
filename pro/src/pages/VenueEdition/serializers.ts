import { EditVenueBodyModel } from 'apiClient/v1'

import { DEFAULT_INTITIAL_OPENING_HOURS } from './constants'
import { VenueEditionFormValues, Day } from './types'

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
  const returnValue: {[day: string]: Array<Array<string>>} = {}
  const days: Day[] = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ]

  if (
    !alreadyHasOpeningHours &&
    days.filter((d) => formValues[d]?.morningEndingHour).length === 0
  ) {
    //  If the opening hours have never been set yet, and if none of the days have a timespan set on the form,
    //  do not set the openingHours in the PATCH on the venue. Otherwise, the venue would appear "closed".
    return null
  }

  for (const day of days) {
    if (!formValues[day]) {
      formValues[day] = DEFAULT_INTITIAL_OPENING_HOURS
    }
    const dayValues = formValues[day]
    const timespan = []
    const morning = []
    const afternoon = []
    if (dayValues.morningStartingHour && dayValues.morningEndingHour) {
      morning.push(dayValues.morningStartingHour, dayValues.morningEndingHour)
      timespan.push(morning)
    }
    if (dayValues.afternoonStartingHour && dayValues.afternoonEndingHour) {
      afternoon.push(
        dayValues.afternoonStartingHour,
        dayValues.afternoonEndingHour
      )
      timespan.push(afternoon)
    }

    if (timespan.length > 0) {
      returnValue[day.toUpperCase()] = timespan
    }
  }

  return returnValue
}
