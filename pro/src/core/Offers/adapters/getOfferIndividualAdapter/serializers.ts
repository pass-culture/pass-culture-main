import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  OfferIndividual,
  OfferIndividualImage,
  OfferIndividualOfferer,
  OfferIndividualStock,
  OfferIndividualVenue,
  OfferIndividualVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeOffererApi = (
  apiOffer: GetIndividualOfferResponseModel
): OfferIndividualOfferer => ({
  id: apiOffer.venue.managingOfferer.id,
  name: apiOffer.venue.managingOfferer.name,
})

export const serializeVenueApi = (
  apiOffer: GetIndividualOfferResponseModel
): OfferIndividualVenue => {
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]:
      apiOffer.venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]:
      apiOffer.venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.venue.motorDisabilityCompliant || false,
  }
  return {
    id: apiOffer.venue.id,
    name: apiOffer.venue.name,
    publicName: apiOffer.venue.publicName || '',
    isVirtual: apiOffer.venue.isVirtual,
    address: apiOffer.venue.address || '',
    postalCode: apiOffer.venue.postalCode || '',
    departmentCode: apiOffer.venue.departementCode || '',
    city: apiOffer.venue.city || '',
    offerer: serializeOffererApi(apiOffer),
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
    },
  }
}

export const serializeStockApi = (
  apiStock: GetOfferStockResponseModel
): OfferIndividualStock => {
  // null or undefined -> 'unlimited', 0 -> 0
  const remainingQuantity = apiStock.remainingQuantity ?? 'unlimited'

  return {
    beginningDatetime: apiStock.beginningDatetime ?? null,
    bookingLimitDatetime: apiStock.bookingLimitDatetime ?? null,
    bookingsQuantity: apiStock.bookingsQuantity,
    dateCreated: new Date(apiStock.dateCreated),
    hasActivationCode: apiStock.hasActivationCode,
    id: apiStock.id,
    isEventDeletable: apiStock.isEventDeletable,
    isEventExpired: apiStock.isEventExpired,
    isSoftDeleted: apiStock.isSoftDeleted,
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

export const serializeLastProvider = (
  apiVenueProvider: GetOfferLastProviderResponseModel | null
): OfferIndividualVenueProvider | null => {
  if (apiVenueProvider === null) {
    return null
  }

  return {
    name: apiVenueProvider.name,
  }
}

export const serializeOfferApiImage = (
  apiOffer: GetIndividualOfferResponseModel
): OfferIndividualImage | undefined => {
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
): OfferIndividual => {
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]: apiOffer.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: apiOffer.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.motorDisabilityCompliant || false,
  }

  const offer: OfferIndividual = {
    id: apiOffer.id,
    bookingEmail: apiOffer.bookingEmail || '',
    bookingContact: apiOffer.bookingContact || '',
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    isActive: apiOffer.isActive,
    isDuo: apiOffer.isDuo,
    isEvent: apiOffer.isEvent,
    isDigital: apiOffer.isDigital,
    isNational: apiOffer.isNational,
    name: apiOffer.name,
    offererId: apiOffer.venue.managingOfferer.id,
    offererName: apiOffer.venue.managingOfferer.name,
    priceCategories: apiOffer.priceCategories,
    subcategoryId: apiOffer.subcategoryId,
    url: apiOffer.url || '',
    externalTicketOfficeUrl: apiOffer.externalTicketOfficeUrl || '',
    venueId: apiOffer.venue.id,
    venue: serializeVenueApi(apiOffer),
    withdrawalDetails: apiOffer.withdrawalDetails || '',
    withdrawalDelay:
      apiOffer.withdrawalDelay === undefined ? null : apiOffer.withdrawalDelay,
    withdrawalType: apiOffer.withdrawalType || null,
    image: serializeOfferApiImage(apiOffer),
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
    },
    stocks: apiOffer.stocks.map(serializeStockApi),
    lastProviderName: apiOffer.lastProvider?.name || null,
    lastProvider: serializeLastProvider(apiOffer.lastProvider || null),
    status: apiOffer.status,
    ...serializeOfferApiExtraData(apiOffer),
  }

  return offer
}
