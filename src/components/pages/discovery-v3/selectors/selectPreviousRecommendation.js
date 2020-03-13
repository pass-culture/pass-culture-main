import createCachedSelector from 're-reselect'

import mapArgsToCacheKey from './mapArgsToCacheKey'
import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectRecommendationsWithLastFakeReco from './selectRecommendationsWithLastFakeRecommendation'

const selectPreviousRecommendation = createCachedSelector(
  selectRecommendationsWithLastFakeReco,
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
)(mapArgsToCacheKey)

export default selectPreviousRecommendation
