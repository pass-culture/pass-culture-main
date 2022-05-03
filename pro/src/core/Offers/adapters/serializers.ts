import { IApiOfferIndividual, IOfferIndividual } from 'core/Offers/types'

export const serializeOfferApi = (
  offerApi: IApiOfferIndividual
): IOfferIndividual => {
  const offer: IOfferIndividual = {
    bookingEmail: offerApi.bookingEmail || '',
    description: offerApi.description || '',
    durationMinutes: offerApi.durationMinutes || null,
    isDuo: offerApi.isDuo,
    isEducational: offerApi.isEducational,
    noDisabilityCompliant: false,
    audioDisabilityCompliant: offerApi.audioDisabilityCompliant || false,
    mentalDisabilityCompliant: offerApi.mentalDisabilityCompliant || false,
    motorDisabilityCompliant: offerApi.motorDisabilityCompliant || false,
    visualDisabilityCompliant: offerApi.visualDisabilityCompliant || false,
    isNational: offerApi.isNational,
    name: offerApi.name,
    offererId: offerApi.venue.managingOffererId,
    subcategoryId: offerApi.subcategoryId,
    url: offerApi.url || '',
    externalTicketOfficeUrl: offerApi.externalTicketOfficeUrl || '',
    venueId: offerApi.venueId,
    withdrawalDetails: offerApi.withdrawalDetails || '',
    withdrawalDelay: offerApi.withdrawalDelay || null,
    // extraData values
    author: offerApi.extraData?.author || '',
    isbn: offerApi.extraData?.isbn || '',
    musicType: offerApi.extraData?.musicType || '',
    musicSubType: offerApi.extraData?.musicSubType || '',
    performer: offerApi.extraData?.performer || '',
    showType: offerApi.extraData?.showType || '',
    showSubType: offerApi.extraData?.showSubType || '',
    speaker: offerApi.extraData?.speaker || '',
    stageDirector: offerApi.extraData?.stageDirector || '',
    visa: offerApi.extraData?.visa || '',
  }

  if (
    [
      offerApi.audioDisabilityCompliant,
      offerApi.mentalDisabilityCompliant,
      offerApi.motorDisabilityCompliant,
      offerApi.visualDisabilityCompliant,
    ].includes(undefined) ||
    [
      offerApi.audioDisabilityCompliant,
      offerApi.mentalDisabilityCompliant,
      offerApi.motorDisabilityCompliant,
      offerApi.visualDisabilityCompliant,
    ].includes(true)
  ) {
    offer.noDisabilityCompliant = false
  } else {
    offer.noDisabilityCompliant = true
  }

  return offer
}
