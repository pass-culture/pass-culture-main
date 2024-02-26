import { ListOffersResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export const serializeOffers = (offers: ListOffersResponseModel): Offer[] =>
  offers.map((offer) => ({
    id: offer.id,
    status: offer.status,
    isActive: offer.isActive,
    hasBookingLimitDatetimesPassed: offer.hasBookingLimitDatetimesPassed,
    thumbUrl: offer.thumbUrl,
    isEducational: offer.isEducational,
    name: offer.name,
    isEvent: offer.isEvent,
    productIsbn: offer.productIsbn,
    venue: offer.venue,
    stocks: offer.stocks,
    isEditable: offer.isEditable,
    isShowcase: offer.isShowcase,
  }))
