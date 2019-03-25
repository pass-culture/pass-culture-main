import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offererId) {
  return offererId || ''
}

export const selectOffererById = createCachedSelector(
  state => state.data.offerers,
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)(mapArgsToCacheKey)

export default selectOffererById
