import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offererId) {
  return offererId || ''
}

const selectOffererById = createCachedSelector(
  state => state.data.offerers,
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)(mapArgsToCacheKey)

export default selectOffererById
