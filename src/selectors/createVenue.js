import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

export default () => createSelector(
  state => createVenuesSelector(),
  (state, venueId) => venueId,
  (venues, venueId) => {
    return venues.find(v => v.id === venueId)
  }
)
