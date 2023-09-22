import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { IndividualOffer, OfferSubCategory } from 'core/Offers/types'

import buildSubcategoryFields from './buildSubCategoryFields'

const serializeDurationHour = (durationMinute: number): string => {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const setInitialFormValues = (
  offer: IndividualOffer,
  subCategoryList: OfferSubCategory[],
  isBookingContactEnabled: boolean
): IndividualOfferFormValues => {
  const subcategory = subCategoryList.find(
    (s: OfferSubCategory) => s.id === offer.subcategoryId
  )

  if (subcategory === undefined) {
    throw Error('La categorie de l’offre est introuvable')
  }

  const { subcategoryFields } = buildSubcategoryFields(
    isBookingContactEnabled,
    subcategory
  )

  return {
    isEvent: offer.isEvent,
    subCategoryFields: subcategoryFields,
    name: offer.name,
    description: offer.description,
    offererId: offer.offererId.toString(),
    venueId: offer.venueId.toString(),
    isNational: offer.isNational,
    isDuo: offer.isDuo,
    categoryId: subcategory.categoryId,
    subcategoryId: offer.subcategoryId,
    showType: offer.showType,
    showSubType: offer.showSubType,
    musicType: offer.musicType,
    musicSubType: offer.musicSubType,
    withdrawalDetails:
      offer.withdrawalDetails || FORM_DEFAULT_VALUES['withdrawalDetails'],
    withdrawalDelay:
      offer.withdrawalDelay === null ? undefined : offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType || undefined,
    accessibility: offer.accessibility,
    bookingEmail: offer.bookingEmail,
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: !!offer.bookingEmail,
    author: offer.author,
    performer: offer.performer,
    ean: offer.ean,
    speaker: offer.speaker,
    stageDirector: offer.stageDirector,
    visa: offer.visa,
    durationMinutes:
      offer.durationMinutes === null
        ? undefined
        : serializeDurationHour(offer.durationMinutes),
    url: offer.url || FORM_DEFAULT_VALUES['url'],
    externalTicketOfficeUrl:
      offer.externalTicketOfficeUrl ||
      FORM_DEFAULT_VALUES['externalTicketOfficeUrl'],
  }
}

export default setInitialFormValues
