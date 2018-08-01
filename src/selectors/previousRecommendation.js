import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'
import uniqueRecommendationsSelector from './uniqueRecommendations'

export default createSelector(
  uniqueRecommendationsSelector,
  currentRecommendationSelector,
  (recommendations, currentRecommendation) => {

    const previousRecommendation = currentRecommendation &&
      get(recommendations, recommendations.findIndex(reco =>
        reco.id === currentRecommendation.id) - 1)

    if (!previousRecommendation) {
      return undefined
    }

    const { mediationId, offerId } = previousRecommendation

    return Object.assign({
      path: `/decouverte/${offerId}/${mediationId || ''}`
    }, previousRecommendation)

  }
)
