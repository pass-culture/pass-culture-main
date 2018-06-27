import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'
const venuesSelector = createVenuesSelector()

export default () => createSelector(
  (state, venueId, offererId) => venuesSelector(state, offererId),
  (state, venueId, offererId) => venueId,
  (venues, venueId) => {
    return venues.find(v => v.id === venueId)
  }
)
