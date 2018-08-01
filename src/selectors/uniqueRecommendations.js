import { createSelector } from 'reselect'

import recommendationsSelector from './recommendations'

export default createSelector(
  recommendationsSelector,
  recommendations => {
    let recosById = {}
    let recoUid = recommendation =>
      recommendation.mediation
        ? recommendation.mediationId
        : 'nomed_' + (recommendation.offer.eventOrThing.id)
    recommendations.forEach(recommendation =>
      (recosById[recoUid(recommendation)] = recommendation))
    return Object.values(recosById)
  }
)
