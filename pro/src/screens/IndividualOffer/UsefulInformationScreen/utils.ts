import {
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm/constants'
import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import {
  CATEGORY_STATUS,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { isOfferSynchronized } from 'core/Offers/utils/synchronization'
import { AccessibilityEnum } from 'core/shared/types'

import { DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES } from './constants'
import { UsefulInformationFormValues } from './types'

export const getFilteredVenueListBySubcategory = (
  venueList: VenueListItemResponseModel[],
  subcategory?: SubcategoryResponseModel
): VenueListItemResponseModel[] => {
  if (!subcategory) {
    return venueList
  }

  if (subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return venueList
  }

  return venueList.filter((venue) =>
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}

interface DefaultInitialValuesFromOfferOptions {
  selectedVenue: VenueListItemResponseModel | undefined
}
export function setDefaultInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  options?: DefaultInitialValuesFromOfferOptions
): UsefulInformationFormValues {
  const baseAccessibility = {
    [AccessibilityEnum.VISUAL]: offer.visualDisabilityCompliant,
    [AccessibilityEnum.MENTAL]: offer.mentalDisabilityCompliant,
    [AccessibilityEnum.AUDIO]: offer.audioDisabilityCompliant,
    [AccessibilityEnum.MOTOR]: offer.motorDisabilityCompliant,
  }

  const notAccessible = Object.values(baseAccessibility).every(
    (value) => value === false
  )

  let addressFields = {}
  if (offer.address) {
    const { street, postalCode, city, latitude, longitude } = offer.address
    const addressAutocomplete = `${street} ${postalCode} ${city}`
    const coords = `${latitude}, ${longitude}`

    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    //  then set this OA id in formik field (so it will be checked by default)
    //  Else, we can assume it's an "other" address
    const offerlocation =
      options?.selectedVenue?.address &&
      options.selectedVenue.address.id_oa === offer.address.id_oa
        ? offer.address.id_oa
        : OFFER_LOCATION.OTHER_ADDRESS

    addressFields = {
      offerlocation: String(offerlocation),
      manuallySetAddress: offer.address.isManualEdition,
      'search-addressAutocomplete': addressAutocomplete,
      addressAutocomplete,
      coords,
      banId: offer.address.banId,
      locationLabel: offer.address.label,
      street: offer.address.street,
      postalCode: offer.address.postalCode,
      city: offer.address.city,
      latitude: String(offer.address.latitude),
      longitude: String(offer.address.longitude),
    }
  }

  return {
    isEvent: offer.isEvent,
    isNational: offer.isNational,
    withdrawalDetails:
      offer.withdrawalDetails ||
      DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['withdrawalDetails'],
    withdrawalDelay:
      offer.withdrawalDelay === null ? undefined : offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType || undefined,
    accessibility: {
      [AccessibilityEnum.VISUAL]: offer.visualDisabilityCompliant || false,
      [AccessibilityEnum.MENTAL]: offer.mentalDisabilityCompliant || false,
      [AccessibilityEnum.AUDIO]: offer.audioDisabilityCompliant || false,
      [AccessibilityEnum.MOTOR]: offer.motorDisabilityCompliant || false,
      [AccessibilityEnum.NONE]: notAccessible,
    },
    bookingEmail: offer.bookingEmail || '',
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: !!offer.bookingEmail,
    url: offer.url || DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['url'],
    isVenueVirtual: offer.venue.isVirtual || false,
    ...addressFields,
  }
}

export function setFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel
): string[] {
  const readOnlyField: string[] = []
  if ([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)) {
    return Object.keys(DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES)
  }

  if (isOfferSynchronized(offer)) {
    const editableFields: string[] = ['accessibility']

    return Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) => !editableFields.includes(field)
    )
  }

  return readOnlyField
}
