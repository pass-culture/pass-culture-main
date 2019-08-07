import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectFirstMatchingBookingByStocks from './selectFirstMatchingBookingByStocks'
import selectOfferById from './selectOfferById'
import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectBookingByMatch = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => {
    return selectOfferById(state, match.params.offerId)
  },
  (bookings, allStocks, booking, offer) => {
    if (booking) {
      return booking
    }

    if (offer) {
      const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, offer.id)
      const firstMatchingBooking = selectFirstMatchingBookingByStocks(
        { data: { bookings } },
        stocks
      )
      return firstMatchingBooking
    }
  }
)(mapArgsToCacheKey)

export default selectBookingByMatch
