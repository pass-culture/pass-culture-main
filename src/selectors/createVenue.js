import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

export default (venuesSelector=createVenuesSelector()) => createSelector(
  (state, venueId, offererId) => venuesSelector(state, offererId),
  (state, venueId, offererId) => venueId,
  (venues, venueId) => {
    return venues.find(v => v.id === venueId)
  }
)
