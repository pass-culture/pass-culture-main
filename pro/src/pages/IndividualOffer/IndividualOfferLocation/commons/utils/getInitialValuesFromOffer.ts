import { computeAddressDisplayName } from 'repository/venuesService'

import type {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import type { Undefinedable } from '@/commons/utils/types'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'

import { OFFER_LOCATION } from '../../../commons/constants'
import { DEFAULT_PHYSICAL_ADDRESS_SUBFORM_INITIAL_VALUES } from '../constants'
import type { LocationFormValues, PhysicalAddressSubformValues } from '../types'

function getPhysicalAddressSubformInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    isOfferSubcategoryOnline,
    offerVenue,
  }: {
    isOfferSubcategoryOnline: boolean
    offerVenue: VenueListItemResponseModel
  }
): Undefinedable<PhysicalAddressSubformValues> {
  if (isOfferSubcategoryOnline) {
    return DEFAULT_PHYSICAL_ADDRESS_SUBFORM_INITIAL_VALUES
  }

  if (offer.address) {
    const { latitude, longitude } = offer.address
    const addressAutocomplete = computeAddressDisplayName(offer.address, false)
    const coords = `${latitude}, ${longitude}`

    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    //  then set this OA id in formik field (so it will be checked by default)
    //  Else, we can assume it's an "other" address
    const offerLocation =
      offerVenue?.address && offerVenue.address.id_oa === offer.address.id_oa
        ? offer.address.id_oa
        : OFFER_LOCATION.OTHER_ADDRESS

    return {
      addressAutocomplete,
      banId: offer.address.banId,
      city: offer.address.city,
      coords,
      inseeCode: offer.address.inseeCode,
      isManualEdition: offer.address.isManualEdition,
      latitude: String(offer.address.latitude),
      locationLabel: offer.address.label,
      longitude: String(offer.address.longitude),
      offerLocation: String(offerLocation),
      postalCode: offer.address.postalCode,
      'search-addressAutocomplete': addressAutocomplete,
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
      latitude: String(offerVenue.address.latitude),
      locationLabel: offerVenue.address.label ?? null,
      longitude: String(offerVenue.address.longitude),
      offerLocation: String(offerVenue.address.id_oa),
      postalCode: offerVenue.address.postalCode,
      'search-addressAutocomplete': null,
      street: offerVenue.address.street ?? null,
    }
  }

  return DEFAULT_PHYSICAL_ADDRESS_SUBFORM_INITIAL_VALUES
}

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    isOfferSubcategoryOnline,
    offerVenue,
  }: {
    offerVenue: VenueListItemResponseModel
    isOfferSubcategoryOnline: boolean
  }
): LocationFormValues {
  const physicalAddressInitialValues =
    getPhysicalAddressSubformInitialValuesFromOffer(offer, {
      isOfferSubcategoryOnline,
      offerVenue,
    })

  // Build initial values without enforcing required constraints at mount time.
  // Normalize URL but allow null (CREATION mode can start without URL for online offers).
  return {
    ...(physicalAddressInitialValues as LocationFormValues),
    url: nonEmptyStringOrNull().cast(offer.url ?? null),
  }
}
