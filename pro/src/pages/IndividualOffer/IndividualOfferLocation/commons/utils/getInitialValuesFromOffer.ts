import { computeAddressDisplayName } from 'repository/venuesService'

import type {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'

import { OFFER_LOCATION } from '../../../commons/constants'
import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../constants'
import type { LocationFormValues, PhysicalAddressSubformValues } from '../types'

// TODO (igabriele, 2025-08-25): Integrate the last rules in Yup schema and use schema.cast() here instead.
function getPhysicalAddressSubformInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    offerVenue,
  }: {
    offerVenue: VenueListItemResponseModel
  }
): PhysicalAddressSubformValues | null {
  if (offer.isDigital) {
    return null
  }

  if (offer.location) {
    const { latitude, longitude } = offer.location
    const addressAutocomplete = computeAddressDisplayName(offer.location, false)
    const coords = `${latitude}, ${longitude}`

    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    //  then set this OA id in form field (so it will be checked by default)
    //  Else, we can assume it's an "other" address
    const offerLocation = offer.location.isVenueLocation
      ? String(offer.location.id)
      : OFFER_LOCATION.OTHER_ADDRESS

    return {
      addressAutocomplete,
      banId: offer.location.banId ?? null,
      city: offer.location.city,
      coords,
      inseeCode: offer.location.inseeCode ?? null,
      isManualEdition: offer.location.isManualEdition,
      isVenueLocation: String(offerLocation) !== OFFER_LOCATION.OTHER_ADDRESS,
      label: offer.location.label ?? null,
      latitude: String(offer.location.latitude),
      longitude: String(offer.location.longitude),
      offerLocation,
      postalCode: offer.location.postalCode,
      'search-addressAutocomplete': addressAutocomplete,
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive an offer address without street since it's mandatory.
      // @ts-expect-error
      street: offer.location.street,
    }
  } else if (offerVenue.location) {
    return {
      addressAutocomplete: null,
      banId: offerVenue.location.banId ?? null,
      city: offerVenue.location.city,
      coords: `${offerVenue.location.latitude}, ${offerVenue.location.longitude}`,
      inseeCode: offerVenue.location.inseeCode ?? null,
      isManualEdition: false,
      isVenueLocation: true,
      label: offerVenue.location.label ?? null,
      latitude: String(offerVenue.location.latitude),
      longitude: String(offerVenue.location.longitude),
      offerLocation: String(offerVenue.location.id),
      postalCode: offerVenue.location.postalCode,
      'search-addressAutocomplete': null,
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive a venue address without street since it's mandatory.

      street: offerVenue.location.street ?? null,
    }
  }

  return EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES
}

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    offerVenue,
  }: {
    offerVenue: VenueListItemResponseModel
  }
): LocationFormValues {
  const physicalAddressInitialValues =
    getPhysicalAddressSubformInitialValuesFromOffer(offer, {
      offerVenue,
    })

  // Build initial values without enforcing required constraints at mount time.
  // Normalize URL but allow null (CREATION mode can start without URL for online offers).
  return {
    location: physicalAddressInitialValues,
    url: offer.url ?? null,
  }
}
