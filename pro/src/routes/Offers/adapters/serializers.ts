import {
  ListOffersOfferResponseModel,
  ListOffersQueryModel,
  ListOffersResponseModel,
} from 'api/v1/gen'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Offer, Stock, Venue, TSearchFilters } from 'core/Offers/types'

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
    beginningDatetime: stock.beginningDatetime,
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

export const serializeApiFilters = <K extends keyof TSearchFilters>(
  searchFilters: TSearchFilters & { page?: number }
): ListOffersQueryModel => {
  const keys = Object.keys(DEFAULT_SEARCH_FILTERS) as K[]

  const body = {} as ListOffersQueryModel

  keys.forEach(field => {
    if (
      searchFilters[field] &&
      searchFilters[field] !== DEFAULT_SEARCH_FILTERS[field]
    ) {
      body[field] = searchFilters[field] as ListOffersQueryModel[typeof field]
    }
  })

  return body
}
