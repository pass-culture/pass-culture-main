import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectFavoriteById from './selectFavoriteById'
import selectOfferById from './selectOfferById'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
}

const selectOfferByMatch = createCachedSelector(
  state => state.data.offers,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (state, match) => selectOfferById(state, match.params.offerId),
  (offers, booking, favorite, offer) => {
    if (offer) {
      return offer
    }
    if (booking) {
      return selectOfferById({ data: { offers } }, booking.stock.offerId)
    }
    if (favorite) {
      return selectOfferById({ data: { offers } }, favorite.offerId)
    }
  }
)(mapArgsToCacheKey)

export default selectOfferByMatch
