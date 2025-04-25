import {
  CollectiveLocationType,
  GetEducationalOffererResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import { OfferEducationalFormValues } from '../types'

export const applyVenueDefaultsToFormValues = (
  values: OfferEducationalFormValues,
  offerer: GetEducationalOffererResponseModel | null,
  isOfferCreated: boolean,
  venues?: VenueListItemResponseModel[]
): OfferEducationalFormValues => {
  const venue = offerer?.managedVenues.find(
    ({ id }) => id.toString() === values.venueId
  )

  const selectedVenue = venues?.find(
    (v) => v.id.toString() === values.venueId.toString()
  )

  if (!venue) {
    return values
  }

  const locationFromSelectedVenue = {
    locationType: CollectiveLocationType.ADDRESS,
    address: {
      isVenueAddress: true,
      id_oa: selectedVenue?.address?.id_oa.toString() ?? '',
      isManualEdition: false,
      label: venue.name,
    },
  }

  const selectedVenueAddress = {
    city: selectedVenue?.address?.city ?? '',
    latitude: selectedVenue?.address?.latitude.toString() ?? '',
    longitude: selectedVenue?.address?.longitude.toString() ?? '',
    postalCode: selectedVenue?.address?.postalCode ?? '',
    street: selectedVenue?.address?.street ?? '',
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
      location:
        // if offer location was the venue address, we set by default the new selected
        // venue address in offer location otherwise we keep former selected location
        values.location.locationType === CollectiveLocationType.ADDRESS &&
        values.location.address.isVenueAddress
          ? locationFromSelectedVenue
          : { ...values.location },
      ...selectedVenueAddress,
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
    location: locationFromSelectedVenue,
    ...selectedVenueAddress,
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
