import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offerId, mediationId) {
  return `${offerId || ''}${mediationId || ''}`
}

export const selectRecommendationByOfferIdAndMediationId = createCachedSelector(
  state => state.data.recommendations,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (recommendations, offerId, mediationId) =>
    recommendations.find(recommendation => {
      const matchOffer = recommendation.offerId === offerId
      const matchMediation = recommendation.mediationId === mediationId
      return matchMediation || matchOffer
    })
)(mapArgsToCacheKey)

export default selectRecommendationByOfferIdAndMediationId
