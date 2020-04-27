import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectIndexifiedRecommendations from './selectIndexifiedRecommendations'
import { createSelector } from 'reselect'

const selectNextRecommendation = createSelector(
  selectIndexifiedRecommendations,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    if (!currentRecommendation) {
      return null
    }

    const nextRecommendation = recommendations.find(
      recommendation => recommendation.index === currentRecommendation.index + 1
    )
    if (!nextRecommendation) {
      return null
    }

    return nextRecommendation
  }
)

export default selectNextRecommendation
