import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectRecommendationsWithLastFakeReco from './selectRecommendationsWithLastFakeReco'
import { createSelector } from 'reselect'

const selectNextRecommendation = createSelector(
  selectRecommendationsWithLastFakeReco,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    if (!currentRecommendation) {
      return null
    }

    const nextRecommendation = recommendations.find(recommendation => recommendation.index === currentRecommendation.index + 1)
    if (!nextRecommendation) {
      return undefined
    }
    const { mediationId, offerId } = nextRecommendation
    const path = `/decouverte/${offerId}/${mediationId || ''}`
    return Object.assign({ path }, nextRecommendation)
  }
)

export default selectNextRecommendation
