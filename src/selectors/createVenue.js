import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

const venuesSelector = createVenuesSelector()

export default () => createSelector(
  state => venuesSelector,
  (state, venueId) => venueId,
  (venues, venueId) => {
    return venues.find(v => v.id === venueId)
  }
)
