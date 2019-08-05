import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectOfferById from './selectOfferById'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
}

const selectOfferByMatch = createCachedSelector(
  state => state.data.offers,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectOfferById(state, match.params.offerId),
  (offers, booking, offer) => {
    if (offer) {
      return offer
    }
    if (booking) {
      return selectOfferById({ data: { offers } }, booking.stock.offerId)
    }
  }
)(mapArgsToCacheKey)

export default selectOfferByMatch
