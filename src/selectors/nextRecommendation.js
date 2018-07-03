import { createSelector } from 'reselect'

import selectSortedRecommendations from './sortedRecommendations'
import selectCurrentRecommendation from './currentRecommendation'
import getRecommendation from '../getters/recommendation'

export default createSelector(
  state => state.data.recommendations || [],
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
