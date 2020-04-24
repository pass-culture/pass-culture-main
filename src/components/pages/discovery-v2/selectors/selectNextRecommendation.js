import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectIndexifiedRecommendations from './selectIndexifiedRecommendations'
import createCachedSelector from 're-reselect'
import mapArgsToCacheKey from './mapArgsToCacheKey'

const selectNextRecommendation = createCachedSelector(
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
)(mapArgsToCacheKey)

export default selectNextRecommendation
