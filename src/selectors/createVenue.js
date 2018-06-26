import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

export default venuesSelector => createSelector(
  venuesSelector,
  (state, venueId) => venueId,
  (venues, venueId) => {
    return venues.find(v => v.id === venueId)
  }
)
