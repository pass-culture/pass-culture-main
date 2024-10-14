import { GetEducationalOffererResponseModel } from 'apiClient/v1'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import { OfferEducationalFormValues } from '../types'

export const applyVenueDefaultsToFormValues = (
  values: OfferEducationalFormValues,
  offerers: GetEducationalOffererResponseModel[],
  isOfferCreated: boolean
): OfferEducationalFormValues => {
  const venue = offerers
    .find(({ id }) => id.toString() === values.offererId)
    ?.managedVenues.find(({ id }) => id.toString() === values.venueId)

  if (!venue) {
    return values
  }

  if (isOfferCreated) {
    //  In this case we are re-opening the first step during creation
    //  If there are venue email and phone and no form email and phone yet, we pre-fill the form inputs
    return {
      ...values,
      email:
        venue.collectiveEmail && !values.email
          ? venue.collectiveEmail
          : values.email,
      phone:
        venue.collectivePhone && !values.phone
          ? venue.collectivePhone
          : values.phone,
    }
  }

  const valuesWithNewVenueFields = {
    ...values,
    interventionArea:
      venue.collectiveInterventionArea ??
      DEFAULT_EAC_FORM_VALUES.interventionArea,
    eventAddress: {
      ...values.eventAddress,
      venueId: Number(values.venueId),
    },
  }

  // Change these fields only if offer is not created yet
  const {
    visualDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    audioDisabilityCompliant,
  } = venue

  const noDisabilityCompliant =
    !visualDisabilityCompliant &&
    !mentalDisabilityCompliant &&
    !motorDisabilityCompliant &&
    !audioDisabilityCompliant

  return {
    ...valuesWithNewVenueFields,
    accessibility: {
      visual: Boolean(visualDisabilityCompliant),
      mental: Boolean(mentalDisabilityCompliant),
      motor: Boolean(motorDisabilityCompliant),
      audio: Boolean(audioDisabilityCompliant),
      none: noDisabilityCompliant,
    },
    email: venue.collectiveEmail ?? values.email,
    phone: venue.collectivePhone ?? values.phone,
    notificationEmails: [venue.collectiveEmail ?? values.email],
  }
}
