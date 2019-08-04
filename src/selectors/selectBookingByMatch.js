import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectFavoriteById from './selectFavoriteById'
import selectFirstMatchingBookingByStocks from './selectFirstMatchingBookingByStocks'
import selectOfferById from './selectOfferById'
import selectRecommendationByOfferIdAndMediationId from './selectRecommendationByOfferIdAndMediationId'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectBookingByMatch = createCachedSelector(
  state => state.data.bookings,
  state => state.data.offers,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (state, match) =>
    selectRecommendationByOfferIdAndMediationId(
      state,
      match.params.offerId,
      match.params.mediationId
    ),
  (bookings, offers, booking, favorite, recommendation) => {
    if (booking) {
      return booking
    }
    if (favorite) {
      const offer = selectOfferById({ data: { offers } }, favorite.offerId)
      const { stocks } = offer || {}
      const firstMatchingBooking = selectFirstMatchingBookingByStocks(
        { data: { bookings } },
        stocks
      )
      return firstMatchingBooking
    }
    if (recommendation) {
      const offer = selectOfferById({ data: { offers } }, recommendation.offerId)
      const { stocks } = offer || {}
      const firstMatchingBooking = selectFirstMatchingBookingByStocks(
        { data: { bookings } },
        stocks
      )
      return firstMatchingBooking
    }
  }
)(mapArgsToCacheKey)

export default selectBookingByMatch
