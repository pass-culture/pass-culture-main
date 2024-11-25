import {
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'commons/core/Offers/constants'
import { isOfferSynchronized } from 'commons/core/Offers/utils/typology'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { FORM_DEFAULT_VALUES, OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { computeAddressDisplayName } from 'repository/venuesService'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from './constants'
import { UsefulInformationFormValues } from './types'

interface SetDefaultInitialValuesFromOfferProps {
  offer: GetIndividualOfferWithAddressResponseModel
  selectedVenue?: VenueListItemResponseModel | undefined
}

export function setDefaultInitialValuesFromOffer({
  offer,
  selectedVenue = undefined,
}: SetDefaultInitialValuesFromOfferProps): UsefulInformationFormValues {
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
      banId: offer.address.banId,
      locationLabel: offer.address.label ?? '',
      street: offer.address.street,
      postalCode: offer.address.postalCode,
      city: offer.address.city,
      latitude: String(offer.address.latitude),
      longitude: String(offer.address.longitude),
    }
  } else if (selectedVenue && selectedVenue.address) {
    addressFields = {
      offerLocation: String(selectedVenue.address.id_oa),
      coords: `${selectedVenue.address.latitude}, ${selectedVenue.address.longitude}`,
      banId: selectedVenue.address.banId,
      locationLabel: selectedVenue.address.label ?? '',
      street: selectedVenue.address.street,
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
      DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES['withdrawalDetails'],
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
    url: offer.url || DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES['url'],
    isVenueVirtual: offer.venue.isVirtual || false,
    ...addressFields,
  }
}

export function setFormReadOnlyFields(
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
