import createCachedSelector from 're-reselect'

import selectBookingByMatch from './selectBookingByMatch'
import selectFavoriteById from './selectFavoriteById'
import selectRecommendationById from './selectRecommendationById'
import selectRecommendationByOfferIdAndMediationId from './selectRecommendationByOfferIdAndMediationId'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectOfferByMatch = createCachedSelector(
  state => state.data.recommendations,
  (state, match) =>
    selectRecommendationByOfferIdAndMediationId(
      state,
      match.params.offerId,
      match.params.mediationId
    ),
  selectBookingByMatch,
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (recommendations, recommendation, booking, favorite) => {
    if (recommendation) {
      return recommendation
    }
    if (booking) {
      return selectRecommendationById({ data: { recommendations } }, booking.recommendationId)
    }
    if (favorite) {
      return selectRecommendationByOfferIdAndMediationId(
        { data: { recommendations } },
        favorite.offerId,
        favorite.mediationId
      )
    }
  }
)(mapArgsToCacheKey)

export default selectOfferByMatch
