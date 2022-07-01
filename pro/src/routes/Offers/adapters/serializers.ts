import {
  ListOffersOfferResponseModel,
  ListOffersResponseModel,
} from 'apiClient/v1'
import { Offer, Stock, Venue } from 'core/Offers/types'

const serializeVenue = (
  venue: ListOffersOfferResponseModel['venue']
): Venue => ({
  name: venue.name,
  publicName: venue.publicName,
  offererName: venue.offererName,
  isVirtual: venue.isVirtual,
  departementCode: venue.departementCode,
})

const serializeStocks = (
  stocks: ListOffersOfferResponseModel['stocks']
): Stock[] =>
  stocks.map(stock => ({
    beginningDatetime: stock.beginningDatetime
      ? new Date(stock.beginningDatetime)
      : null,
    remainingQuantity: stock.remainingQuantity,
  }))

export const serializeOffers = (offers: ListOffersResponseModel): Offer[] =>
  offers.map(offer => ({
    id: offer.id,
    status: offer.status,
    isActive: offer.isActive,
    hasBookingLimitDatetimesPassed: offer.hasBookingLimitDatetimesPassed,
    thumbUrl: offer.thumbUrl,
    isEducational: offer.isEducational,
    name: offer.name,
    isEvent: offer.isEvent,
    productIsbn: offer.productIsbn,
    venue: serializeVenue(offer.venue),
    stocks: serializeStocks(offer.stocks),
    isEditable: offer.isEditable,
    isShowcase: offer.isShowcase,
  }))
