import { computeAddressDisplayName } from 'repository/venuesService'

import {
  type GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  type SubcategoryResponseModel,
  type VenueListItemResponseModel,
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
import type { UsefulInformationFormValues } from './types'

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  {
    offerSubcategory,
    selectedVenue = undefined,
  }: {
    selectedVenue?: VenueListItemResponseModel | undefined
    offerSubcategory?: SubcategoryResponseModel
  }
): UsefulInformationFormValues {
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
    accessibility: getAccessibilityFormValuesFromOffer(offer),
    ...addressFields,
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

// Temporary clone of `src/pages/IndividualOffer/commons/getOfferConditionalFields.ts`
// that will disappear with this entire page once `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` FF is enabled in production.
/** @deprecated */
/* istanbul ignore next: see above comment */
export const getOfferConditionalFields = ({
  offerSubCategory = null,
  receiveNotificationEmails = null,
}: {
  offerSubCategory?: SubcategoryResponseModel | null
  receiveNotificationEmails?: boolean | null
}): string[] => {
  const offerConditionalFields = []

  if (offerSubCategory?.isEvent) {
    offerConditionalFields.push('durationMinutes')
  }

  if (offerSubCategory?.canBeDuo) {
    offerConditionalFields.push('isDuo')
  }

  if (offerSubCategory?.conditionalFields.includes('musicType')) {
    offerConditionalFields.push('musicSubType')
  }

  if (offerSubCategory?.conditionalFields.includes('showType')) {
    offerConditionalFields.push('showSubType')
  }

  if (receiveNotificationEmails) {
    offerConditionalFields.push('bookingEmail')
  }

  if (offerSubCategory?.canBeWithdrawable) {
    offerConditionalFields.push('withdrawalType')
    offerConditionalFields.push('withdrawalDelay')
    offerConditionalFields.push('bookingContact')
  }

  return offerConditionalFields
}
