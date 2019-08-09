import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectFavoriteById from './selectFavoriteById'
import selectMediationById from './selectMediationById'
import selectRecommendationById from './selectRecommendationById'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId } = params

  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}`
}

const selectMediationByMatch = createCachedSelector(
  state => state.data.mediations,
  state => state.data.recommendations,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (state, match) => selectMediationById(state, match.params.mediationId),
  (mediations, recommendations, booking, favorite, mediation) => {
    if (mediation) return mediation

    if (booking && booking.recommendationId) {
      const recommendation = selectRecommendationById(
        { data: { recommendations } },
        booking.recommendationId
      )

      return selectMediationById({ data: { mediations } }, recommendation.mediationId)
    }

    if (favorite) {
      return selectMediationById({ data: { mediations } }, favorite.mediationId)
    }
  }
)(mapArgsToCacheKey)

export default selectMediationByMatch
