import createCachedSelector from 're-reselect'

import selectRecommendationsForDiscovery from '../recommendationsForDiscovery'

export const selectCurrentRecommendation = createCachedSelector(
  selectRecommendationsForDiscovery,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (allRecommendations, offerId, mediationId) => {
    const currentRecommendation = allRecommendations.find(recommendation => {
      const matchOffer = recommendation.offerId === offerId
      const matchMediation = recommendation.mediationId === mediationId
      return offerId === 'tuto' ? matchMediation : matchOffer
    })
    return currentRecommendation
  }
)(
  (state, offerId, mediationId, position) =>
    `${offerId || ''}/${mediationId || ''}/${position || ''}`
)

export default selectCurrentRecommendation
