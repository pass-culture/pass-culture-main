import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'
import recommendationsSelector from './recommendations'
// import uniqueRecommendationsSelector from './uniqueRecommendations'

export default createSelector(
  recommendationsSelector,
  currentRecommendationSelector,
  (recommendations, currentRecommendation) => {
    const nextRecommendation = currentRecommendation &&
      get(recommendations, recommendations.findIndex(recommendation =>
        recommendation.id === currentRecommendation.id) + 1)

    if (!nextRecommendation) {
      return undefined
    }

    const { mediationId, offerId } = nextRecommendation

    return Object.assign({
      path: `/decouverte/${offerId}/${mediationId || ''}`
    }, nextRecommendation)
  }
)
