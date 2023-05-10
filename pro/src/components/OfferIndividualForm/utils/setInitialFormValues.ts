import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'

import buildSubCategoryFields from './buildSubCategoryFields'

const serializeDurationHour = (durationMinute: number): string => {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const setInitialFormValues = (
  offer: IOfferIndividual,
  subCategoryList: IOfferSubCategory[]
): IOfferIndividualFormValues => {
  const subCategory = subCategoryList.find(
    (s: IOfferSubCategory) => s.id === offer.subcategoryId
  )

  if (subCategory === undefined) {
    throw Error('La categorie de l’offre est introuvable')
  }

  const { subCategoryFields } = buildSubCategoryFields(
    offer.subcategoryId,
    subCategoryList
  )

  return {
    isEvent: offer.isEvent,
    subCategoryFields: subCategoryFields,
    name: offer.name,
    description: offer.description,
    offererId: offer.offererId.toString(),
    venueId: offer.venueId.toString(),
    isNational: offer.isNational,
    isDuo: offer.isDuo,
    categoryId: subCategory.categoryId,
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
    receiveNotificationEmails: !!offer.bookingEmail,
    author: offer.author,
    isbn: offer.isbn,
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
