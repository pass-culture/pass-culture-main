import { createSelector } from 'reselect'


export default createSelector(
  state => state.data.recommendations || [],
  (recommendations) => {
    let recosById = {}
    let recoUid = r => r.mediation ? r.mediationId : 'nomed_'+(r.thingId || r.eventId);
    recommendations.forEach(r => recosById[recoUid(r)] = r)
    return Object.values(recosById)
  }
)
