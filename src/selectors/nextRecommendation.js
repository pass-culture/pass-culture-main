import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'
import getRecommendation from '../getters/recommendation'

export default createSelector(
  state => state.data.recommendations,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    const nextRecommendation =
      currentRecommendation &&
      recommendations &&
      recommendations[
        recommendations.findIndex(um => um.id === currentRecommendation.id) + 1
      ]
    return getRecommendation({ recommendation: nextRecommendation })
  }
)
