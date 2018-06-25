import { createSelector } from 'reselect'

import createVenueSelect from './createVenues'

export default createSelector(
  createVenueSelect(),
  venues => venues && venues.map(v =>
      ({ label: v.name, value: v.id }))
)
