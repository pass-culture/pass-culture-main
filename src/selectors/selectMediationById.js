import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, mediationId) {
  return mediationId || ''
}

export const selectMediationById = createCachedSelector(
  state => state.data.mediations,
  (state, mediationId) => mediationId,
  (mediations, mediationId) => mediations.find(mediation => mediation.id === mediationId)
)(mapArgsToCacheKey)

export default selectMediationById
