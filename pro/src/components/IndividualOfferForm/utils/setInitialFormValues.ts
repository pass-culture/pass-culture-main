import {
  GetIndividualOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { AccessiblityEnum } from 'core/shared'

import buildSubcategoryFields from './buildSubCategoryFields'

const serializeDurationHour = (durationMinute: number): string => {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const setInitialFormValues = (
  offer: GetIndividualOfferResponseModel,
  subCategoryList: SubcategoryResponseModel[],
  isBookingContactEnabled: boolean
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
    [AccessiblityEnum.VISUAL]: offer.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: offer.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: offer.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: offer.motorDisabilityCompliant || false,
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
    gtl_id: offer.extraData?.gtl_id || '',
    musicType: offer.extraData?.musicType || '',
    musicSubType: offer.extraData?.musicSubType || '',
    withdrawalDetails:
      offer.withdrawalDetails || FORM_DEFAULT_VALUES['withdrawalDetails'],
    withdrawalDelay:
      offer.withdrawalDelay === null ? undefined : offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType || undefined,
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
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
        : serializeDurationHour(offer.durationMinutes),
    url: offer.url || FORM_DEFAULT_VALUES['url'],
    externalTicketOfficeUrl:
      offer.externalTicketOfficeUrl ||
      FORM_DEFAULT_VALUES['externalTicketOfficeUrl'],
  }
}

export default setInitialFormValues
