import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
} from 'core/Offers/types'

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

export const serializeOfferApi = (
  apiOffer: GetIndividualOfferResponseModel
): IOfferIndividual => {
  const offer: IOfferIndividual = {
    id: apiOffer.id,
    nonHumanizedId: apiOffer.nonHumanizedId,
    bookingEmail: apiOffer.bookingEmail || '',
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    isDuo: apiOffer.isDuo,
    isEvent: apiOffer.isEvent,
    isEducational: apiOffer.isEducational,
    noDisabilityCompliant: false,
    audioDisabilityCompliant: apiOffer.audioDisabilityCompliant || false,
    mentalDisabilityCompliant: apiOffer.mentalDisabilityCompliant || false,
    motorDisabilityCompliant: apiOffer.motorDisabilityCompliant || false,
    visualDisabilityCompliant: apiOffer.visualDisabilityCompliant || false,
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
    // extraData values
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
    stocks: apiOffer.stocks.map(serializeStockApi),
  }

  if (
    [
      apiOffer.audioDisabilityCompliant,
      apiOffer.mentalDisabilityCompliant,
      apiOffer.motorDisabilityCompliant,
      apiOffer.visualDisabilityCompliant,
    ].includes(undefined) ||
    [
      apiOffer.audioDisabilityCompliant,
      apiOffer.mentalDisabilityCompliant,
      apiOffer.motorDisabilityCompliant,
      apiOffer.visualDisabilityCompliant,
    ].includes(true)
  ) {
    offer.noDisabilityCompliant = false
  } else {
    offer.noDisabilityCompliant = true
  }

  return offer
}
