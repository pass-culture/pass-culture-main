import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  IndividualOffer,
  IndividualOfferImage,
  IndividualOfferStock,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeStockApi = (
  apiStock: GetOfferStockResponseModel
): IndividualOfferStock => {
  // null or undefined -> 'unlimited', 0 -> 0
  const remainingQuantity = apiStock.remainingQuantity ?? 'unlimited'

  return {
    beginningDatetime: apiStock.beginningDatetime ?? null,
    bookingLimitDatetime: apiStock.bookingLimitDatetime ?? null,
    bookingsQuantity: apiStock.bookingsQuantity,
    hasActivationCode: apiStock.hasActivationCode,
    id: apiStock.id,
    isEventDeletable: apiStock.isEventDeletable,
    price: apiStock.price,
    priceCategoryId: apiStock.priceCategoryId,
    quantity: apiStock.quantity,
    remainingQuantity: remainingQuantity,
    activationCodesExpirationDatetime:
      apiStock.activationCodesExpirationDatetime
        ? new Date(apiStock.activationCodesExpirationDatetime)
        : null,
    activationCodes: [],
  }
}

export const serializeOfferApiExtraData = (
  apiOffer: GetIndividualOfferResponseModel
) => ({
  author: apiOffer.extraData?.author || '',
  musicType: apiOffer.extraData?.musicType || '',
  musicSubType: apiOffer.extraData?.musicSubType || '',
  performer: apiOffer.extraData?.performer || '',
  ean: apiOffer.extraData?.ean || '',
  showType: apiOffer.extraData?.showType || '',
  showSubType: apiOffer.extraData?.showSubType || '',
  speaker: apiOffer.extraData?.speaker || '',
  stageDirector: apiOffer.extraData?.stageDirector || '',
  visa: apiOffer.extraData?.visa || '',
})

export const serializeOfferApiImage = (
  apiOffer: GetIndividualOfferResponseModel
): IndividualOfferImage | undefined => {
  if (apiOffer.activeMediation) {
    if (apiOffer.activeMediation.thumbUrl) {
      return {
        originalUrl: apiOffer.activeMediation.thumbUrl,
        url: apiOffer.activeMediation.thumbUrl,
        credit: apiOffer.activeMediation?.credit || '',
      }
    }
  } else if (apiOffer.thumbUrl) {
    // synchronized offers have thumbUrl but no mediation
    return {
      originalUrl: apiOffer.thumbUrl,
      url: apiOffer.thumbUrl,
      credit: '',
    }
  }
  return undefined
}

export const serializeOfferApi = (
  apiOffer: GetIndividualOfferResponseModel
): IndividualOffer => {
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]: apiOffer.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: apiOffer.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.motorDisabilityCompliant || false,
  }

  const offer: IndividualOffer = {
    id: apiOffer.id,
    bookingEmail: apiOffer.bookingEmail || '',
    bookingContact: apiOffer.bookingContact || '',
    bookingsCount: apiOffer.bookingsCount || 0,
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    hasStocks: apiOffer.hasStocks,
    isActive: apiOffer.isActive,
    isActivable: apiOffer.isActivable,
    isDuo: apiOffer.isDuo,
    isEvent: apiOffer.isEvent,
    isDigital: apiOffer.isDigital,
    isNational: apiOffer.isNational,
    name: apiOffer.name,
    priceCategories: apiOffer.priceCategories,
    subcategoryId: apiOffer.subcategoryId,
    url: apiOffer.url || '',
    externalTicketOfficeUrl: apiOffer.externalTicketOfficeUrl || '',
    venue: apiOffer.venue,
    withdrawalDetails: apiOffer.withdrawalDetails || '',
    withdrawalDelay:
      apiOffer.withdrawalDelay === undefined ? null : apiOffer.withdrawalDelay,
    withdrawalType: apiOffer.withdrawalType || null,
    image: serializeOfferApiImage(apiOffer),
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
    },
    lastProviderName: apiOffer.lastProvider?.name || null,
    lastProvider: apiOffer.lastProvider,
    status: apiOffer.status,
    ...serializeOfferApiExtraData(apiOffer),
  }

  return offer
}
