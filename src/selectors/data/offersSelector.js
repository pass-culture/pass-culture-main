import createCachedSelector from 're-reselect'

import selectBookingById from '../selectBookingById'
import selectOfferById from '../selectOfferById'
import selectStockById from '../selectStockById'

export const selectOffers = state => state.data.offers

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params

  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
}

export const selectOfferByRouterMatch = createCachedSelector(
  state => state.data.offers,
  state => state.data.stocks,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectOfferById(state, match.params.offerId),
  (offers, stocks, booking, offer) => {
    if (offer) return offer

    if (booking) {
      const stock = selectStockById({ data: { stocks } }, booking.stockId)

      return selectOfferById({ data: { offers } }, stock.offerId)
    }
  }
)(mapArgsToCacheKey)
