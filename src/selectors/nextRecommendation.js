import { createSelector } from 'reselect'

import selectSortedRecommendations from './sortedRecommendations'
import selectCurrentRecommendation from './currentRecommendation'
import getRecommendation from '../getters/recommendation'
import selectUniqueRecommendations from './uniqueRecommendations'

export default createSelector(
  selectUniqueRecommendations,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    const nextRecommendation =
      currentRecommendation &&
      recommendations &&
      recommendations[
        recommendations.findIndex(reco =>
          reco.id === currentRecommendation.id) + 1
      ]
    return getRecommendation({ recommendation: nextRecommendation })
  }
)
