import selectIndexifiedRecommendations from './selectIndexifiedRecommendations'
import { createSelector } from 'reselect'

const selectCurrentRecommendation = createSelector(
  selectIndexifiedRecommendations,
  (state, offerId) => offerId,
  (recommendations, offerId) =>
    recommendations.find(recommendation => {
      return offerId === recommendation.offerId
    })
)

export default selectCurrentRecommendation
