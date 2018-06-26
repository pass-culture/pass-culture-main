import { createSelector } from 'reselect'


export default mediationsSelector => createSelector(
  mediationsSelector,
  (state, mediationId) => mediationId,
  (mediations, mediationId) => {
    return mediations.filter(m => m.id === mediationId)
  }
)
