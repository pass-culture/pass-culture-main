import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectRecommendationsWithLastFakeReco from './selectRecommendationsWithLastFakeReco'
import createCachedSelector from 're-reselect'
import mapArgsToCacheKey from './mapArgsToCacheKey'

const selectNextRecommendation = createCachedSelector(
  selectRecommendationsWithLastFakeReco,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    if (!currentRecommendation) {
      return null
    }

    const nextRecommendation = recommendations.find(recommendation => recommendation.index === currentRecommendation.index + 1)
    if (!nextRecommendation) {
      return null
    }
    const { mediationId, offerId } = nextRecommendation
    const path = `/decouverte/${offerId}/${mediationId || ''}`
    return Object.assign({ path }, nextRecommendation)
  }
)(mapArgsToCacheKey)

export default selectNextRecommendation
