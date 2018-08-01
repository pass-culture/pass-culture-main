import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'
import uniqueRecommendationsSelector from './uniqueRecommendations'

export default createSelector(
  uniqueRecommendationsSelector,
  currentRecommendationSelector,
  (recommendations, currentRecommendation) =>
    currentRecommendation &&
    recommendations &&
    recommendations[
      recommendations.findIndex(
        reco => reco.id === currentRecommendation.id
      ) + 1
    ]
)
