import createCachedSelector from 're-reselect'

import mapArgsToCacheKey from './mapArgsToCacheKey'
import selectUniqAndIndexifiedRecommendations from './selectUniqAndIndexifiedRecommendations'

const selectCurrentRecommendation = createCachedSelector(
  selectUniqAndIndexifiedRecommendations,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (recommendations, offerId, mediationId) =>
    recommendations.find(recommendation => {
      const matchOffer = recommendation.offerId === offerId
      const matchMediation = recommendation.mediationId === mediationId
      return offerId === 'tuto' ? matchMediation : matchOffer
    })
)(mapArgsToCacheKey)

export default selectCurrentRecommendation
