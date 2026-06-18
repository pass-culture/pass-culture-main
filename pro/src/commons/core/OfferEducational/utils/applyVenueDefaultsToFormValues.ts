import {
  CollectiveLocationType,
  type GetVenueResponseModel,
} from '@/apiClient/v1'

import { getDefaultEducationalValues } from '../constants'
import type { OfferEducationalFormValues } from '../types'

export const applyVenueDefaultsToFormValues = (
  values: OfferEducationalFormValues,
  isOfferCreated: boolean,
  selectedVenue: GetVenueResponseModel
): OfferEducationalFormValues => {
  const locationFromSelectedVenue = {
    locationType: CollectiveLocationType.ADDRESS,
    location: {
      isVenueLocation: true,
      id: selectedVenue?.location?.id.toString() ?? '',
      isManualEdition: false,
      label: selectedVenue?.publicName,
    },
  }

  const selectedVenueAddress = {
    city: selectedVenue?.location?.city ?? '',
    latitude: selectedVenue?.location?.latitude.toString() ?? '',
    longitude: selectedVenue?.location?.longitude.toString() ?? '',
    postalCode: selectedVenue?.location?.postalCode ?? '',
    street: selectedVenue?.location?.street ?? '',
  }
  const isVenueAddress =
    values.location?.locationType === CollectiveLocationType.ADDRESS &&
    values.location.location?.isVenueLocation

  if (isOfferCreated) {
    //  In this case we are re-opening the first step during creation
    //  If there are venue email and phone and no form email and phone yet, we pre-fill the form inputs
    return {
      ...values,
      contactEmail:
        selectedVenue.collectiveEmail && !values.contactEmail
          ? selectedVenue.collectiveEmail
          : values.contactEmail,
      phone:
        selectedVenue.collectivePhone && !values.phone
          ? selectedVenue.collectivePhone
          : values.phone,
      location:
        // if offer location was the venue address, we set by default the new selected
        // venue address in offer location otherwise we keep former selected location
        isVenueAddress ? locationFromSelectedVenue : { ...values.location },
      ...(isVenueAddress && selectedVenueAddress),
    }
  }

  const valuesWithNewVenueFields = {
    ...values,
    interventionArea:
      selectedVenue.collectiveInterventionArea ??
      getDefaultEducationalValues().interventionArea,
    location: locationFromSelectedVenue,
    ...selectedVenueAddress,
  }

  // Change these fields only if offer is not created yet
  const {
    visualDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    audioDisabilityCompliant,
  } = selectedVenue

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
    contactEmail: selectedVenue.collectiveEmail ?? values.contactEmail,
    phone: selectedVenue.collectivePhone ?? values.phone,
    bookingEmails: [
      { email: selectedVenue.collectiveEmail ?? values.contactEmail ?? '' },
    ],
  }
}
