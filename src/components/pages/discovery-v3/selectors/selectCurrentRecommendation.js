import selectIndexifiedRecommendations from './selectIndexifiedRecommendations'
import createCachedSelector from 're-reselect'
import mapArgsToCacheKey from './mapArgsToCacheKey'

const selectCurrentRecommendation = createCachedSelector(
  selectIndexifiedRecommendations,
  (state, offerId) => offerId,
  (recommendations, offerId) =>
    recommendations.find(recommendation => {
      return offerId === recommendation.offerId
    })
)(mapArgsToCacheKey)

export default selectCurrentRecommendation
