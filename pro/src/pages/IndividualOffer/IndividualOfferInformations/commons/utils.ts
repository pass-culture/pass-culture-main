import { computeAddressDisplayName } from 'repository/venuesService'

import {
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from '@/commons/core/Offers/constants'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import {
  FORM_DEFAULT_VALUES,
  OFFER_LOCATION,
} from '@/pages/IndividualOffer/commons/constants'
import { getAccessibilityFormValuesFromOffer } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from './constants'
import { UsefulInformationFormValues } from './types'

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    isNewOfferCreationFlowFeatureActive,
    offerSubcategory,
    selectedVenue = undefined,
  }: {
    selectedVenue?: VenueListItemResponseModel | undefined
    offerSubcategory?: SubcategoryResponseModel
    isNewOfferCreationFlowFeatureActive: boolean
  }
): UsefulInformationFormValues {
  const maybeAccessibility = isNewOfferCreationFlowFeatureActive
    ? {}
    : { accessibility: getAccessibilityFormValuesFromOffer(offer) }

  let addressFields = {}

  if (offer.address) {
    const { latitude, longitude } = offer.address
    const addressAutocomplete = computeAddressDisplayName(offer.address, false)
    const coords = `${latitude}, ${longitude}`

    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    //  then set this OA id in formik field (so it will be checked by default)
    //  Else, we can assume it's an "other" address
    const offerLocation =
      selectedVenue?.address &&
      selectedVenue.address.id_oa === offer.address.id_oa
        ? offer.address.id_oa
        : OFFER_LOCATION.OTHER_ADDRESS

    addressFields = {
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
  } else if (!offer.isDigital && selectedVenue && selectedVenue.address) {
    addressFields = {
      offerLocation: String(selectedVenue.address.id_oa),
      coords: `${selectedVenue.address.latitude}, ${selectedVenue.address.longitude}`,
      banId: selectedVenue.address.banId ?? '',
      inseeCode: selectedVenue.address.inseeCode ?? '',
      locationLabel: selectedVenue.address.label ?? '',
      street: selectedVenue.address.street ?? '',
      postalCode: selectedVenue.address.postalCode,
      city: selectedVenue.address.city,
      latitude: String(selectedVenue.address.latitude),
      longitude: String(selectedVenue.address.longitude),
    }
  }

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
    ...addressFields,
    ...maybeAccessibility,
  }
}

export function getFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel
): string[] {
  const readOnlyField: string[] = []
  if ([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)) {
    return Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
  }

  if (isOfferSynchronized(offer)) {
    const editableFields: string[] = ['accessibility']

    return Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) => !editableFields.includes(field)
    )
  }

  return readOnlyField
}
