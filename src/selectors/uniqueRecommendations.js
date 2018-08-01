import { createSelector } from 'reselect'

import recommendationsSelector from './recommendations'

export default createSelector(
  recommendationsSelector,
  recommendations => {
    let recosById = {}
    let recoUid = r =>
      r.mediation ? r.mediationId : 'nomed_' + (r.thingId || r.eventId)
    recommendations.forEach(r => (recosById[recoUid(r)] = r))
    return Object.values(recosById)
  }
)
