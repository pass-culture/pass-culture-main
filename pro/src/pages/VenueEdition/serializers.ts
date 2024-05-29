import { EditVenueBodyModel } from 'apiClient/v1'

import { VenueEditionFormValues, Day } from './types'

export const serializeEditVenueBodyModel = (
  formValues: VenueEditionFormValues,
  hideSiret: boolean
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
    isEmailAppliedOnAllOffers: true,
    isAccessibilityAppliedOnAllOffers:
      formValues.isAccessibilityAppliedOnAllOffers,
    openingHours: serializeOpeningHours(formValues),
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}

function serializeOpeningHours(
  formValues: VenueEditionFormValues
): EditVenueBodyModel['openingHours'] {
  const returnValue = []
  const days: Day[] = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ]
  for (const day of days) {
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

    returnValue.push({
      weekday: day,
      timespan,
    })
  }

  return returnValue
}
