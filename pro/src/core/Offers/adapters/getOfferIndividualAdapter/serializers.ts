import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeOffererApi = (
  apiOffer: GetIndividualOfferResponseModel
): IOfferIndividualOfferer => {
  return {
    id: apiOffer.venue.managingOfferer.id,
    name: apiOffer.venue.managingOfferer.name,
  }
}

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
): IOfferIndividualStock => {
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
    offerId: apiStock.offerId,
    price: apiStock.price,
    quantity: apiStock.quantity,
    remainingQuantity: apiStock.remainingQuantity ?? 0,
  }
}

export const serializeOfferApiExtraData = (
  apiOffer: GetIndividualOfferResponseModel
) => {
  return {
    author: apiOffer.extraData?.author || '',
    isbn: apiOffer.extraData?.isbn || '',
    musicType: apiOffer.extraData?.musicType || '',
    musicSubType: apiOffer.extraData?.musicSubType || '',
    performer: apiOffer.extraData?.performer || '',
    showType: apiOffer.extraData?.showType || '',
    showSubType: apiOffer.extraData?.showSubType || '',
    speaker: apiOffer.extraData?.speaker || '',
    stageDirector: apiOffer.extraData?.stageDirector || '',
    visa: apiOffer.extraData?.visa || '',
  }
}

export const serializeLastProvider = (
  apiVenueProvider: GetOfferLastProviderResponseModel | null
): IOfferIndividualVenueProvider | null => {
  if (apiVenueProvider === null) {
    return null
  }

  return {
    id: apiVenueProvider.id,
    isActive: apiVenueProvider.isActive,
    name: apiVenueProvider.name,
  }
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
    id: apiOffer.id,
    nonHumanizedId: apiOffer.nonHumanizedId,
    bookingEmail: apiOffer.bookingEmail || '',
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    isDuo: apiOffer.isDuo,
    isEvent: apiOffer.isEvent,
    isEducational: apiOffer.isEducational,
    isNational: apiOffer.isNational,
    name: apiOffer.name,
    offererId: apiOffer.venue.managingOffererId,
    subcategoryId: apiOffer.subcategoryId,
    url: apiOffer.url || '',
    externalTicketOfficeUrl: apiOffer.externalTicketOfficeUrl || '',
    venueId: apiOffer.venueId,
    venue: serializeVenueApi(apiOffer),
    withdrawalDetails: apiOffer.withdrawalDetails || '',
    withdrawalDelay: apiOffer.withdrawalDelay || null,
    withdrawalType: apiOffer.withdrawalType || null,
    thumbUrl: apiOffer.thumbUrl || '',
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
    },
    stocks: apiOffer.stocks.map(serializeStockApi),
    lastProviderName: apiOffer.lastProvider?.name || null,
    lastProvider: serializeLastProvider(apiOffer.lastProvider || null),
    status: apiOffer.status || null,
    ...serializeOfferApiExtraData(apiOffer),
  }

  return offer
}
