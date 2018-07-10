import createCachedSelector from 're-reselect';

import venuesSelector from './venues'

export default createCachedSelector(
  (state) => venuesSelector(state),
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)(
  (state, venueId) => venueId || ''
)
