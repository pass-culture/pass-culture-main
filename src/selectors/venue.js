import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.venues,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)((state, venueId) => venueId || '')
