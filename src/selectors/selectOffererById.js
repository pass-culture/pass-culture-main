import createCachedSelector from 're-reselect'
import selectOfferers from './selectOfferers'

function mapArgsToCacheKey(state, offererId) {
  return offererId || ''
}

const selectOffererById = createCachedSelector(
  selectOfferers,
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)(mapArgsToCacheKey)

export default selectOffererById
