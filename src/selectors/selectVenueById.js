import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, venueId) {
  return venueId || ''
}

export const selectVenueById = createCachedSelector(
  state => state.data.venues,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)(mapArgsToCacheKey)

export default selectVenueById
