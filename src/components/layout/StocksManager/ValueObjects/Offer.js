export default class Offer {
  constructor(offer = {}) {
    this.bookingEmail = offer.bookingEmail
    this.dateCreated = offer.dateCreated
    this.dateModifiedAtLastProvider = offer.dateModifiedAtLastProvider
    this.isEvent = offer.isEvent
    this.isThing = offer.isThing
    this.id = offer.id
    this.idAtProviders = offer.idAtProviders
    this.isActive = offer.isActive
    this.lastProvider = offer.lastProvider || null
    this.lastProviderId = offer.lastProviderId
    this.mediationsIds = offer.mediationsIds
    this.modelName = offer.modelName
    this.productId = offer.productId
    this.stocksIds = offer.stocksIds
    this.venueId = offer.venueId
  }

  get hasBeenProvidedByAllocine() {
    return !!(this.lastProvider && this.lastProvider.name === 'Allociné')
  }
}
