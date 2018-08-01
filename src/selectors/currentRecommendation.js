import get from 'lodash.get'
import { createSelector } from 'reselect'

import recommendationsSelector from './recommendations'

export default createSelector(
  recommendationsSelector,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (recommendations, offerId, mediationId) => {
    let filteredRecommendations

    if (mediationId) {
      filteredRecommendations = recommendations.filter(
        m => m.mediationId === mediationId
      )
    } else {
      filteredRecommendations = recommendations
    }

    // special tuto case
    let recommendation
    if (offerId === 'tuto') {
      recommendation = get(filteredRecommendations, '0')
    } else {
      recommendation = filteredRecommendations.find(r => r.offerId === offerId)
    }

    return recommendation
  }
)
