import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectRecommendationsWithLastFakeReco from './selectRecommendationsWithLastFakeRecommendation'
import createCachedSelector from 're-reselect'
import mapArgsToCacheKey from './mapArgsToCacheKey'

const selectNextRecommendation = createCachedSelector(
  selectRecommendationsWithLastFakeReco,
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
