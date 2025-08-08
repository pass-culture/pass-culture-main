import { computeAddressDisplayName } from 'repository/venuesService'

import {
  type GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import { getAccessibilityFormValuesFromOffer } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'

import { OFFER_LOCATION } from '../../commons/constants'
import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from './constants'
import { UsefulInformationFormValues } from './types'

function getAddressFieldsFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    isNewOfferCreationFlowFeatureActive,
    isOfferSubcategoryOnline,
    offerVenue,
  }: {
    isNewOfferCreationFlowFeatureActive: boolean
    isOfferSubcategoryOnline: boolean
    offerVenue: VenueListItemResponseModel
  }
): Partial<UsefulInformationFormValues> {
  if (
    (isNewOfferCreationFlowFeatureActive && isOfferSubcategoryOnline) ||
    (!isNewOfferCreationFlowFeatureActive && offer.isDigital)
  ) {
    return {}
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
      offerLocation: String(offerLocation),
      manuallySetAddress: offer.address.isManualEdition,
      'search-addressAutocomplete': addressAutocomplete,
      addressAutocomplete,
      coords,
      banId: offer.address.banId ?? '',
      inseeCode: offer.address.inseeCode ?? '',
      locationLabel: offer.address.label ?? '',
      street: offer.address.street ?? '',
      postalCode: offer.address.postalCode,
      city: offer.address.city,
      latitude: String(offer.address.latitude),
      longitude: String(offer.address.longitude),
    }
  } else if (offerVenue?.address) {
    return {
      offerLocation: String(offerVenue.address.id_oa),
      manuallySetAddress: false,
      coords: `${offerVenue.address.latitude}, ${offerVenue.address.longitude}`,
      banId: offerVenue.address.banId ?? '',
      inseeCode: offerVenue.address.inseeCode ?? '',
      locationLabel: offerVenue.address.label ?? '',
      street: offerVenue.address.street ?? '',
      postalCode: offerVenue.address.postalCode,
      city: offerVenue.address.city,
      latitude: String(offerVenue.address.latitude),
      longitude: String(offerVenue.address.longitude),
    }
  }

  return {}
}

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    isNewOfferCreationFlowFeatureActive,
    isOfferSubcategoryOnline,
    offerSubcategory,
    offerVenue,
  }: {
    offerVenue: VenueListItemResponseModel
    offerSubcategory: SubcategoryResponseModel
    isNewOfferCreationFlowFeatureActive: boolean
    isOfferSubcategoryOnline: boolean
  }
): UsefulInformationFormValues {
  const maybeAccessibility = isNewOfferCreationFlowFeatureActive
    ? {}
    : { accessibility: getAccessibilityFormValuesFromOffer(offer) }

  let maybeAddress = getAddressFieldsFromOffer(offer, {
    isNewOfferCreationFlowFeatureActive,
    isOfferSubcategoryOnline,
    offerVenue,
  })

  return {
    isEvent: offer.isEvent,
    isNational: offer.isNational,
    withdrawalDetails:
      offer.withdrawalDetails ||
      DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.withdrawalDetails,
    withdrawalDelay:
      offer.withdrawalDelay === null
        ? undefined
        : offer.withdrawalDelay?.toString(),
    withdrawalType:
      offer.withdrawalType ||
      (offerSubcategory?.canBeWithdrawable
        ? WithdrawalTypeEnum.NO_TICKET
        : undefined),
    bookingEmail: offer.bookingEmail || '',
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: !!offer.bookingEmail,
    externalTicketOfficeUrl: offer.externalTicketOfficeUrl || undefined,
    ...maybeAddress,
    ...maybeAccessibility,
  }
}
