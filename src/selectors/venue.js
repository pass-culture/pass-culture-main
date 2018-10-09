import createCachedSelector from 're-reselect'

function mapArgsToKey(state, venueId) {
  return venueId || ''
}

export default createCachedSelector(
  state => state.data.venues,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)(mapArgsToKey)
