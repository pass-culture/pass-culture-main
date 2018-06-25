import get from 'lodash.get'
import { createSelector } from 'reselect'

import createVenueSelect from './createVenues'

export default () => createSelector(
  createVenueSelect,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(v => v.id === venueId)
)
