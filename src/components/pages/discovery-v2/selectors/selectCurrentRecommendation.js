import selectUniqAndIndexifiedRecommendations from './selectUniqAndIndexifiedRecommendations'
import createCachedSelector from 're-reselect'
import mapArgsToCacheKey from './mapArgsToCacheKey'

const selectCurrentRecommendation = createCachedSelector(
  selectUniqAndIndexifiedRecommendations,
  (state, offerId) => offerId,
  (recommendations, offerId) =>
    recommendations.find(recommendation => {
      return offerId === recommendation.offerId
    })
)(mapArgsToCacheKey)

export default selectCurrentRecommendation
