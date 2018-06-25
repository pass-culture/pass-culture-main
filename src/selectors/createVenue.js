import get from 'lodash.get'
import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

export default () => createSelector(
  createVenuesSelector(),
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)
