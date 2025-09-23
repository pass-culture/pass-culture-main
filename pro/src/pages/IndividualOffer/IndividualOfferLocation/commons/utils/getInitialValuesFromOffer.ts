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

  if (offer.address) {
    const { latitude, longitude } = offer.address
    const addressAutocomplete = computeAddressDisplayName(offer.address, false)
    const coords = `${latitude}, ${longitude}`

    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    //  then set this OA id in form field (so it will be checked by default)
    //  Else, we can assume it's an "other" address
    const offerLocation =
      offerVenue?.address && offerVenue.address.id_oa === offer.address.id_oa
        ? offer.address.id_oa
        : OFFER_LOCATION.OTHER_ADDRESS

    return {
      addressAutocomplete,
      banId: offer.address.banId ?? null,
      city: offer.address.city,
      coords,
      inseeCode: offer.address.inseeCode ?? null,
      isManualEdition: offer.address.isManualEdition,
      isVenueAddress: String(offerLocation) !== OFFER_LOCATION.OTHER_ADDRESS,
      label: offer.address.label ?? null,
      latitude: String(offer.address.latitude),
      longitude: String(offer.address.longitude),
      offerLocation: String(offerLocation),
      postalCode: offer.address.postalCode,
      'search-addressAutocomplete': addressAutocomplete,
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive an offer address without street since it's mandatory.
      // @ts-expect-error
      street: offer.address.street,
    }
  } else if (offerVenue.address) {
    return {
      addressAutocomplete: null,
      banId: offerVenue.address.banId ?? null,
      city: offerVenue.address.city,
      coords: `${offerVenue.address.latitude}, ${offerVenue.address.longitude}`,
      inseeCode: offerVenue.address.inseeCode ?? null,
      isManualEdition: false,
      isVenueAddress: true,
      label: offerVenue.address.label ?? null,
      latitude: String(offerVenue.address.latitude),
      longitude: String(offerVenue.address.longitude),
      offerLocation: String(offerVenue.address.id_oa),
      postalCode: offerVenue.address.postalCode,
      'search-addressAutocomplete': null,
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive a venue address without street since it's mandatory.
      // @ts-expect-error
      street: offerVenue.address.street ?? null,
    }
  }

  // @ts-expect-error We have to initialize with empty values when we don't have an address.
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
    address: physicalAddressInitialValues,
    url: offer.url ?? null,
  }
}
