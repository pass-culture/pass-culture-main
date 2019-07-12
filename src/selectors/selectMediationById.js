import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, mediationId) {
  return mediationId || ''
}

const selectMediationById = createCachedSelector(
  state => state.data.mediations,
  (state, mediationId) => mediationId,
  (mediations, mediationId) => mediations.find(m => m.id === mediationId)
)(mapArgsToCacheKey)

export default selectMediationById
