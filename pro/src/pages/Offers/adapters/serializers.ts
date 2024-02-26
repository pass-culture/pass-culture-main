import {
  ListOffersOfferResponseModel,
  ListOffersResponseModel,
} from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import { Offer, Stock } from 'core/Offers/types'

const serializeStocks = (
  stocks: ListOffersOfferResponseModel['stocks']
): Stock[] =>
  stocks.map((stock) => ({
    beginningDatetime: stock.beginningDatetime
      ? new Date(stock.beginningDatetime)
      : null,
    remainingQuantity: stock.remainingQuantity,
    bookingQuantity: stock?.bookingQuantity,
  }))

export const serializeOffers = (offers: ListOffersResponseModel): Offer[] =>
  offers.map((offer) => ({
    id: offer.id,
    // FIX ME: api should send OfferStatus
    status: offer.status as OfferStatus,
    isActive: offer.isActive,
    hasBookingLimitDatetimesPassed: offer.hasBookingLimitDatetimesPassed,
    thumbUrl: offer.thumbUrl,
    isEducational: offer.isEducational,
    name: offer.name,
    isEvent: offer.isEvent,
    productIsbn: offer.productIsbn,
    venue: offer.venue,
    stocks: serializeStocks(offer.stocks),
    isEditable: offer.isEditable,
    isShowcase: offer.isShowcase,
  }))
