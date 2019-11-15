import createCachedSelector from 're-reselect'

import { selectStockById } from './stocksSelectors'
import { selectBookingById } from './bookingsSelectors'

const selectOffers = state => state.data.offers

export const selectOfferById = createCachedSelector(
  selectOffers,
  (state, offerId) => offerId,
  (offers, offerId) => offers.find(offer => offer.id === offerId)
)((state, offerId = '') => offerId)

export const selectOfferByRouterMatch = createCachedSelector(
  selectOffers,
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
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params

  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
})
