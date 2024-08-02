import {
  GetIndividualOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { AccessibilityEnum } from 'core/shared/types'
import { deSerializeDurationMinutes } from 'screens/IndividualOffer/DetailsScreen/utils'

import { FORM_DEFAULT_VALUES } from '../constants'
import { OFFER_LOCATION } from '../OfferLocation/constants'
import { IndividualOfferFormValues } from '../types'

import { buildSubcategoryFields } from './buildSubCategoryFields'

export const setInitialFormValues = (
  offer: GetIndividualOfferResponseModel,
  subCategoryList: SubcategoryResponseModel[],
  isBookingContactEnabled: boolean,
  isOfferAddressEnabled?: boolean,
  isPhysicalEvent?: boolean
): IndividualOfferFormValues => {
  const subcategory = subCategoryList.find(
    (s: SubcategoryResponseModel) => s.id === offer.subcategoryId
  )

  if (subcategory === undefined) {
    throw Error('La categorie de l’offre est introuvable')
  }

  const { subcategoryFields } = buildSubcategoryFields(
    isBookingContactEnabled,
    subcategory
  )

  const baseAccessibility = {
    [AccessibilityEnum.VISUAL]: offer.visualDisabilityCompliant || false,
    [AccessibilityEnum.MENTAL]: offer.mentalDisabilityCompliant || false,
    [AccessibilityEnum.AUDIO]: offer.audioDisabilityCompliant || false,
    [AccessibilityEnum.MOTOR]: offer.motorDisabilityCompliant || false,
  }

  return {
    isEvent: offer.isEvent,
    subCategoryFields: subcategoryFields,
    name: offer.name,
    description: offer.description || '',
    offererId: offer.venue.managingOfferer.id.toString(),
    venueId: offer.venue.id.toString(),
    isNational: offer.isNational,
    isDuo: offer.isDuo,
    categoryId: subcategory.categoryId,
    subcategoryId: offer.subcategoryId,
    showType: offer.extraData?.showType || '',
    showSubType: offer.extraData?.showSubType || '',
    gtl_id: offer.extraData?.gtl_id
      ? offer.extraData?.gtl_id.substring(0, 2) + '000000'
      : '',
    musicType: offer.extraData?.musicType || '',
    musicSubType: offer.extraData?.musicSubType || '',
    withdrawalDetails:
      offer.withdrawalDetails || FORM_DEFAULT_VALUES['withdrawalDetails'],
    withdrawalDelay:
      offer.withdrawalDelay === null ? undefined : offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType || undefined,
    accessibility: {
      ...baseAccessibility,
      [AccessibilityEnum.NONE]:
        !Object.values(baseAccessibility).includes(true),
    },
    bookingEmail: offer.bookingEmail || '',
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: !!offer.bookingEmail,
    author: offer.extraData?.author || '',
    performer: offer.extraData?.performer || '',
    ean: offer.extraData?.ean || '',
    speaker: offer.extraData?.speaker || '',
    stageDirector: offer.extraData?.stageDirector || '',
    visa: offer.extraData?.visa || '',
    durationMinutes:
      offer.durationMinutes === null || offer.durationMinutes === undefined
        ? undefined
        : deSerializeDurationMinutes(offer.durationMinutes),
    url: offer.url || FORM_DEFAULT_VALUES['url'],
    externalTicketOfficeUrl:
      offer.externalTicketOfficeUrl ||
      FORM_DEFAULT_VALUES['externalTicketOfficeUrl'],
    // TODO: Fill that with offer data when available in API
    ...(isOfferAddressEnabled && isPhysicalEvent
      ? {
          offerlocation: OFFER_LOCATION.OTHER_ADDRESS,
          locationLabel: '',
          manuallySetAddress: true,
          street: '',
          'search-addressAutocomplete': '',
          addressAutocomplete: '',
          postalCode: '',
          city: '',
          coords: '',
          latitude: '',
          longitude: '',
          banId: '',
        }
      : {}),
  }
}
