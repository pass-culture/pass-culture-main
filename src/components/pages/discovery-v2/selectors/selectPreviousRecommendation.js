import { createSelector } from 'reselect'

import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectIndexifiedRecommendations from './selectIndexifiedRecommendations'

const selectPreviousRecommendation = createSelector(
  selectIndexifiedRecommendations,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    let previousRecommendation = null
    if (currentRecommendation) {
      const currentRecommendationIndex = recommendations.findIndex(
        recommendation => recommendation.id === currentRecommendation.id
      )
      previousRecommendation =
        currentRecommendation && recommendations[currentRecommendationIndex - 1]
    }

    if (!previousRecommendation) {
      return null
    }

    return previousRecommendation
  }
)

export default selectPreviousRecommendation
