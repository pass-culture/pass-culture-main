import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualImage,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeOffererApi = (
  apiOffer: GetIndividualOfferResponseModel
): IOfferIndividualOfferer => ({
  nonHumanizedId: apiOffer.venue.managingOfferer.nonHumanizedId,
  name: apiOffer.venue.managingOfferer.name,
})

export const serializeVenueApi = (
  apiOffer: GetIndividualOfferResponseModel
): IOfferIndividualVenue => {
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]:
      apiOffer.venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]:
      apiOffer.venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.venue.motorDisabilityCompliant || false,
  }
  return {
    id: apiOffer.venue.nonHumanizedId,
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
): IOfferIndividualStock => {
  // null or undefined -> 'unlimited', 0 -> 0
  const remainingQuantity = apiStock.remainingQuantity ?? 'unlimited'

  return {
    beginningDatetime: apiStock.beginningDatetime ?? null,
    bookingLimitDatetime: apiStock.bookingLimitDatetime ?? null,
    bookingsQuantity: apiStock.bookingsQuantity,
    dateCreated: new Date(apiStock.dateCreated),
    hasActivationCode: apiStock.hasActivationCode,
    nonHumanizedId: apiStock.nonHumanizedId,
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
  isbn: apiOffer.extraData?.isbn || '',
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
): IOfferIndividualVenueProvider | null => {
  if (apiVenueProvider === null) {
    return null
  }

  return {
    name: apiVenueProvider.name,
  }
}

export const serializeOfferApiImage = (
  apiOffer: GetIndividualOfferResponseModel
): IOfferIndividualImage | undefined => {
  if (apiOffer.mediations?.length > 0) {
    const mediation = apiOffer.mediations[0]
    if (mediation.thumbUrl) {
      return {
        originalUrl: mediation.thumbUrl,
        url: mediation.thumbUrl,
        credit: mediation?.credit || '',
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
): IOfferIndividual => {
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]: apiOffer.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: apiOffer.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.motorDisabilityCompliant || false,
  }

  const offer: IOfferIndividual = {
    nonHumanizedId: apiOffer.nonHumanizedId,
    bookingEmail: apiOffer.bookingEmail || '',
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    isActive: apiOffer.isActive,
    isDuo: apiOffer.isDuo,
    isEvent: apiOffer.isEvent,
    isDigital: apiOffer.isDigital,
    isEducational: apiOffer.isEducational,
    isNational: apiOffer.isNational,
    name: apiOffer.name,
    offererId: apiOffer.venue.managingOfferer.nonHumanizedId,
    offererName: apiOffer.venue.managingOfferer.name,
    priceCategories: apiOffer.priceCategories,
    subcategoryId: apiOffer.subcategoryId,
    url: apiOffer.url || '',
    externalTicketOfficeUrl: apiOffer.externalTicketOfficeUrl || '',
    venueId: apiOffer.venue.nonHumanizedId,
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
